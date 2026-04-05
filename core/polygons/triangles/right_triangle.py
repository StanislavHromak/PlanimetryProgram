import math
from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class RightTriangleSolver(GeometricSolver):
    """Розв'язувач задач для прямокутного трикутника."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.c = float(params.get('c', 0))

    def validate(self) -> bool:
        if self.task_type == "RIGHT_LEGS":
            if self.a <= 0 or self.b <= 0:
                self._add_error("Катети мають бути додатними.")
                return False
        elif self.task_type == "RIGHT_LEG_HYPOTENUSE":
            if self.a <= 0 or self.c <= 0:
                self._add_error("Сторони мають бути додатними.")
                return False
            if self.a >= self.c:
                self._add_error("Катет не може бути більшим або рівним гіпотенузі.")
                return False
        return True

    def _compute_hypotenuse(self) -> float:
        if 'c' in self._computed:
            return self._computed['c']

        if self.task_type == "RIGHT_LEGS":
            value = math.sqrt(self.a ** 2 + self.b ** 2)
        else:
            value = self.c

        if not self._is_target("side") and self.task_type == "RIGHT_LEGS":
            self._add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо гіпотенузу",
                "c = √(a² + b²)",
                f"c = √({self.a}² + {self.b}²)",
                value,
                rule="Теорема Піфагора: у прямокутному трикутнику квадрат гіпотенузи "
                     "дорівнює сумі квадратів катетів.",
                is_intermediate=True
            )
            self.step_num += 1

        self._computed['c'] = value
        return value

    def _compute_second_leg(self) -> float:
        if 'b' in self._computed:
            return self._computed['b']

        value = math.sqrt(self.c ** 2 - self.a ** 2)

        if not self._is_target("side"):
            self._add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо другий катет",
                "b = √(c² - a²)",
                f"b = √({self.c}² - {self.a}²)",
                value,
                rule="Теорема Піфагора: у прямокутному трикутнику квадрат гіпотенузи "
                     "дорівнює сумі квадратів катетів.",
                is_intermediate=True
            )
            self.step_num += 1

        self._computed['b'] = value
        return value

    def _calculate(self):
        self.step_num = 1
        result = {}
        plot_b = 0.0
        c = 0.0

        if self.task_type == "RIGHT_LEGS":
            self._add_info(f"Прямокутний трикутник: катети a={self.a}, b={self.b}")

            if self._is_target("side"):
                c = self._compute_hypotenuse()
                result["side_c"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо гіпотенузу",
                    "c = √(a² + b²)",
                    f"c = √({self.a}² + {self.b}²)",
                    c,
                    rule="Теорема Піфагора: у прямокутному трикутнику квадрат гіпотенузи дорівнює сумі квадратів катетів."
                )
                self.step_num += 1

            if self._is_target("area"):
                result["area"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо площу",
                    "S = (a · b) / 2",
                    f"S = ({self.a} · {self.b}) / 2",
                    (self.a * self.b) / 2,
                    rule="Площа прямокутного трикутника дорівнює половині добутку катетів."
                )
                self.step_num += 1

            if self._is_target("perimeter"):
                c = self._compute_hypotenuse()
                result["perimeter"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо периметр",
                    "P = a + b + c",
                    f"P = {self.a} + {self.b} + {c:.2f}",
                    self.a + self.b + c,
                    rule="Периметр трикутника — сума довжин усіх його сторін."
                )
                self.step_num += 1

            if self._is_target("incircle"):
                c = self._compute_hypotenuse()
                result["r_inscribed"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо радіус вписаного кола",
                    "r = (a + b - c) / 2",
                    f"r = ({self.a} + {self.b} - {c:.2f}) / 2",
                    (self.a + self.b - c) / 2,
                    rule="У прямокутному трикутнику радіус вписаного кола: r = (a + b - c) / 2."
                )
                self.step_num += 1

            if self._is_target("circumcircle"):
                c = self._compute_hypotenuse()
                result["r_circumscribed"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо радіус описаного кола",
                    "R = c / 2",
                    f"R = {c:.2f} / 2",
                    c / 2,
                    rule="У прямокутному трикутнику описане коло будується на гіпотенузі як на діаметрі, тому R = c / 2."
                )

            c = self._compute_hypotenuse()
            plot_b = self.b

        elif self.task_type == "RIGHT_LEG_HYPOTENUSE":
            self._add_info(f"Прямокутний трикутник: катет a={self.a}, гіпотенуза c={self.c}")

            if self._is_target("side"):
                b = self._compute_second_leg()
                result["side_b"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо другий катет",
                    "b = √(c² - a²)",
                    f"b = √({self.c}² - {self.a}²)",
                    b,
                    rule="Теорема Піфагора: у прямокутному трикутнику квадрат гіпотенузи дорівнює сумі квадратів катетів."
                )
                self.step_num += 1

            if self._is_target("area"):
                b = self._compute_second_leg()
                result["area"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо площу",
                    "S = (a · b) / 2",
                    f"S = ({self.a} · {b:.2f}) / 2",
                    (self.a * b) / 2,
                    rule="Площа прямокутного трикутника дорівнює половині добутку катетів."
                )
                self.step_num += 1

            if self._is_target("perimeter"):
                b = self._compute_second_leg()
                result["perimeter"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо периметр",
                    "P = a + b + c",
                    f"P = {self.a} + {b:.2f} + {self.c}",
                    self.a + b + self.c,
                    rule="Периметр трикутника — сума довжин усіх його сторін."
                )
                self.step_num += 1

            if self._is_target("incircle"):
                b = self._compute_second_leg()
                result["r_inscribed"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо радіус вписаного кола",
                    "r = (a + b - c) / 2",
                    f"r = ({self.a} + {b:.2f} - {self.c}) / 2",
                    (self.a + b - self.c) / 2,
                    rule="У прямокутному трикутнику радіус вписаного кола: r = (a + b - c) / 2."
                )
                self.step_num += 1

            if self._is_target("circumcircle"):
                result["r_circumscribed"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо радіус описаного кола",
                    "R = c / 2",
                    f"R = {self.c} / 2",
                    self.c / 2,
                    rule="У прямокутному трикутнику описане коло будується на гіпотенузі як на діаметрі, тому R = c / 2."
                )

            plot_b = self._compute_second_leg()
            c = self.c

        image_base64 = TrianglePlotter(self.a, plot_b, c).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
