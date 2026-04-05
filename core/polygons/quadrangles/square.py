import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rectangle_plotter import RectanglePlotter


class SquareSolver(GeometricSolver):
    """Розв'язувач задач з квадратом."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.S = float(params.get('S', 0))
        self.P = float(params.get('P', 0))
        self.d = float(params.get('d', 0))

    def validate(self) -> bool:
        if self.task_type == "SQUARE_SIDE" and self.a <= 0:
            self._add_error("Сторона має бути додатною.")
            return False
        elif self.task_type == "SQUARE_AREA" and self.S <= 0:
            self._add_error("Площа має бути додатною.")
            return False
        elif self.task_type == "SQUARE_PERIMETER" and self.P <= 0:
            self._add_error("Периметр має бути додатним.")
            return False
        elif self.task_type == "SQUARE_DIAGONAL" and self.d <= 0:
            self._add_error("Діагональ має бути додатною.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            error_msg = self._steps[-1]["text"] if isinstance(self._steps[-1], dict) else self._steps[-1]
            return {"success": False, "error": error_msg}

        result = {}
        step_num = 1
        show_diagonal = False
        show_circumcircle = False

        if self.task_type == "SQUARE_SIDE":
            self._add_info(f"Квадрат: a={self.a}")

        elif self.task_type == "SQUARE_AREA":
            self._add_info(f"Квадрат: S={self.S}")
            a_val = math.sqrt(self.S)
            is_int = not self._is_target("side_a")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_side_a" if is_int else "side_a"

            result[key] = self._add_step(
                f"Крок {step_num}. {pref}Знаходимо сторону a",
                "a = √S",
                f"a = √{self.S}",
                a_val,
                rule="Сторона квадрата дорівнює квадратному кореню з його площі.",
                is_intermediate=is_int
            )
            step_num += 1
            self.a = a_val

        elif self.task_type == "SQUARE_PERIMETER":
            self._add_info(f"Квадрат: P={self.P}")
            a_val = self.P / 4
            is_int = not self._is_target("side_a")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_side_a" if is_int else "side_a"

            result[key] = self._add_step(
                f"Крок {step_num}. {pref}Знаходимо сторону a",
                "a = P / 4",
                f"a = {self.P} / 4",
                a_val,
                rule="Оскільки всі сторони квадрата рівні, сторона дорівнює чверті периметра.",
                is_intermediate=is_int
            )
            step_num += 1
            self.a = a_val

        elif self.task_type == "SQUARE_DIAGONAL":
            self._add_info(f"Квадрат: d={self.d}")
            show_diagonal = True
            a_val = self.d / math.sqrt(2)
            is_int = not self._is_target("side_a")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_side_a" if is_int else "side_a"

            result[key] = self._add_step(
                f"Крок {step_num}. {pref}Знаходимо сторону a",
                "a = d / √2",
                f"a = {self.d} / √2",
                a_val,
                rule="Сторона квадрата виражається через діагональ з теореми Піфагора.",
                is_intermediate=is_int
            )
            step_num += 1
            self.a = a_val

        if self._is_target("area") and self.task_type != "SQUARE_AREA":
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу",
                "S = a²",
                f"S = {self.a:.2f}²",
                self.a ** 2,
                rule="Площа квадрата дорівнює квадрату його сторони."
            )
            step_num += 1

        if self._is_target("perimeter") and self.task_type != "SQUARE_PERIMETER":
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = 4 · a",
                f"P = 4 · {self.a:.2f}",
                4 * self.a,
                rule="Периметр квадрата дорівнює сумі чотирьох його сторін."
            )
            step_num += 1

        needs_diagonal = self._is_target("diagonal") or self._is_target("circumcircle")
        if needs_diagonal and self.task_type != "SQUARE_DIAGONAL":
            diag_val = self.a * math.sqrt(2)
            is_int = not self._is_target("diagonal")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_diagonal" if is_int else "diagonal"

            result[key] = self._add_step(
                f"Крок {step_num}. {pref}Знаходимо діагональ d",
                "d = a · √2",
                f"d = {self.a:.2f} · √2",
                diag_val,
                rule="Діагональ квадрата знаходиться за теоремою Піфагора (d² = a² + a²)." if not is_int else "Діагональ необхідна для знаходження радіуса описаного кола.",
                is_intermediate=is_int
            )
            step_num += 1
            self.d = diag_val
            if not is_int:
                show_diagonal = True

        if self._is_target("incircle"):
            r_incircle = self.a / 2
            result["incircle"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус вписаного кола r",
                "r = a / 2",
                f"r = {self.a:.2f} / 2",
                r_incircle,
                rule="Радіус вписаного в квадрат кола дорівнює половині його сторони."
            )
            step_num += 1

        if self._is_target("circumcircle"):
            show_circumcircle = True
            show_diagonal = True
            r_circum = self.d / 2
            result["circumcircle"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус описаного кола R",
                "R = d / 2",
                f"R = {self.d:.2f} / 2",
                r_circum,
                rule="Радіус описаного кола дорівнює половині діагоналі."
            )
            step_num += 1

        # Використовуємо RectanglePlotter, передаючи a=a, b=a
        image_base64 = RectanglePlotter(
            self.a, self.a,
            d=self.d if show_diagonal else None,
            R_circum=self.d / 2 if show_circumcircle else None
        ).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}