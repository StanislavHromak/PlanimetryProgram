import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rectangle_plotter import RectanglePlotter


class RectangleSolver(GeometricSolver):
    """Розв'язувач задач з прямокутником."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        # Зчитуємо всі можливі параметри
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.S = float(params.get('S', 0))
        self.P = float(params.get('P', 0))
        self.d = float(params.get('d', 0))

    def validate(self) -> bool:
        if self.task_type == "RECTANGLE_SIDES":
            if self.a <= 0 or self.b <= 0:
                self._add_error("Сторони прямокутника мають бути додатними.")
                return False
        elif self.task_type == "RECTANGLE_AREA_SIDE":
            if self.a <= 0 or self.S <= 0:
                self._add_error("Сторона та площа мають бути додатними.")
                return False
        elif self.task_type == "RECTANGLE_PERIMETER_SIDE":
            if self.a <= 0 or self.P <= 0:
                self._add_error("Сторона та периметр мають бути додатними.")
                return False
            if self.P <= 2 * self.a:
                self._add_error("Периметр має бути більшим за подвоєну відому сторону.")
                return False
        elif self.task_type == "RECTANGLE_DIAGONAL_SIDE":
            if self.a <= 0 or self.d <= 0:
                self._add_error("Сторона та діагональ мають бути додатними.")
                return False
            if self.d <= self.a:
                self._add_error("Діагональ має бути більшою за будь-яку сторону прямокутника.")
                return False
        return True

    def _calculate(self):
        result = {}
        step_num = 1
        show_diagonal = False
        show_circumcircle = False
        diag_val = self.d if self.d > 0 else 0.0

        if self.task_type == "RECTANGLE_SIDES":
            self._add_info(f"Прямокутник: a={self.a}, b={self.b}")

        elif self.task_type == "RECTANGLE_AREA_SIDE":
            self._add_info(f"Прямокутник: a={self.a}, S={self.S}")
            b_val = self.S / self.a

            is_intermediate = "side_b" not in self.targets
            prefix = "(Проміжний крок) " if is_intermediate else ""
            key = "intermediate_side_b" if is_intermediate else "side_b"

            result[key] = self._add_step(
                f"Крок {step_num}. {prefix}Знаходимо сторону b",
                "b = S / a",
                f"b = {self.S} / {self.a}",
                b_val,
                rule="Друга сторона прямокутника дорівнює площі, поділеній на відому сторону.",
                is_intermediate=is_intermediate
            )
            step_num += 1
            self.b = b_val

        elif self.task_type == "RECTANGLE_PERIMETER_SIDE":
            self._add_info(f"Прямокутник: a={self.a}, P={self.P}")
            b_val = (self.P / 2) - self.a

            is_intermediate = "side_b" not in self.targets
            prefix = "(Проміжний крок) " if is_intermediate else ""
            key = "intermediate_side_b" if is_intermediate else "side_b"

            result[key] = self._add_step(
                f"Крок {step_num}. {prefix}Знаходимо сторону b",
                "b = P / 2 - a",
                f"b = {self.P} / 2 - {self.a}",
                b_val,
                rule="Півпериметр дорівнює сумі суміжних сторін. Віднімаємо відому сторону від півпериметра.",
                is_intermediate=is_intermediate
            )
            step_num += 1
            self.b = b_val

        elif self.task_type == "RECTANGLE_DIAGONAL_SIDE":
            self._add_info(f"Прямокутник: a={self.a}, d={self.d}")
            show_diagonal = True
            b_val = math.sqrt(self.d ** 2 - self.a ** 2)

            is_intermediate = "side_b" not in self.targets
            prefix = "(Проміжний крок) " if is_intermediate else ""
            key = "intermediate_side_b" if is_intermediate else "side_b"

            result[key] = self._add_step(
                f"Крок {step_num}. {prefix}Знаходимо сторону b",
                "b = √(d² - a²)",
                f"b = √({self.d}² - {self.a}²)",
                b_val,
                rule="За теоремою Піфагора для прямокутного трикутника, утвореного діагоналлю та сторонами.",
                is_intermediate=is_intermediate
            )
            step_num += 1
            self.b = b_val

        # ---------------------------------------------------------------- #
        #  БЛОК 2: ОБЧИСЛЕННЯ ЦІЛЬОВИХ ПАРАМЕТРІВ (ТЕПЕР МИ ЗНАЄМО a і b) #
        # ---------------------------------------------------------------- #

        # Площа (не рахуємо, якщо вона була вхідним параметром)
        if "area" in self.targets and self.task_type != "RECTANGLE_AREA_SIDE":
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу прямокутника",
                "S = a · b",
                f"S = {self.a:.2f} · {self.b:.2f}",
                self.a * self.b,
                rule="Площа прямокутника дорівнює добутку його суміжних сторін."
            )
            step_num += 1

        # Периметр (не рахуємо, якщо він був вхідним параметром)
        if "perimeter" in self.targets and self.task_type != "RECTANGLE_PERIMETER_SIDE":
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = 2 · (a + b)",
                f"P = 2 · ({self.a:.2f} + {self.b:.2f})",
                2 * (self.a + self.b),
                rule="Периметр дорівнює подвоєній сумі суміжних сторін."
            )
            step_num += 1

        # Діагональ (як ціль АБО як проміжний крок для кола)
        needs_diagonal = "diagonal" in self.targets or "circumcircle" in self.targets

        if needs_diagonal and self.task_type != "RECTANGLE_DIAGONAL_SIDE":
            diag_val = math.sqrt(self.a ** 2 + self.b ** 2)
            is_intermediate = "diagonal" not in self.targets
            prefix = "(Проміжний крок) " if is_intermediate else ""
            key = "intermediate_diagonal" if is_intermediate else "diagonal"

            result[key] = self._add_step(
                f"Крок {step_num}. {prefix}Знаходимо діагональ d",
                "d = √(a² + b²)",
                f"d = √({self.a:.2f}² + {self.b:.2f}²)",
                diag_val,
                rule="Діагональ прямокутника знаходиться за теоремою Піфагора." if not is_intermediate else "Діагональ потрібна для знаходження радіуса описаного кола.",
                is_intermediate=is_intermediate
            )
            step_num += 1
            if not is_intermediate:
                show_diagonal = True

        # Описане коло
        if "circumcircle" in self.targets:
            show_circumcircle = True
            show_diagonal = True
            r_circum = diag_val / 2
            result["r_circumscribed"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус описаного кола R",
                "R = d / 2",
                f"R = {diag_val:.2f} / 2",
                r_circum,
                rule="Центр описаного кола лежить на перетині діагоналей, а радіус дорівнює половині діагоналі."
            )
            step_num += 1

        # Плоттер малює фігуру (плоттер залишається тим самим, що я давав раніше!)
        image_base64 = RectanglePlotter(
            self.a, self.b,
            d=diag_val if show_diagonal else None,
            R_circum=diag_val / 2 if show_circumcircle else None
        ).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}