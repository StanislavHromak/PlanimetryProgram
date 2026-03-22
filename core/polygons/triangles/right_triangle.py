import math
from core.base import GeometricSolver
from plotters.triangle_plotter import TrianglePlotter


class RightTriangleSolver(GeometricSolver):
    """
    Розвязувач задач для прямокутного трикутника.
    """

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))  # катет 1
        self.b = float(params.get('b', 0))  # катет 2
        self.c = float(params.get('c', 0))  # гіпотенуза

    def validate(self) -> bool:
        if self.task_type == "RIGHT_LEGS":
            if self.a <= 0 or self.b <= 0:
                self._steps.append("Помилка: Катети мають бути додатними.")
                return False
        elif self.task_type == "RIGHT_LEG_HYPOTENUSE":
            if self.a <= 0 or self.c <= 0:
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
            if self.a >= self.c:
                self._steps.append("Помилка: Катет не може бути більшим або рівним гіпотенузі.")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}

        if self.task_type == "RIGHT_LEGS":
            self._steps.append(f"Фігура: Прямокутний трикутник з катетами a={self.a}, b={self.b}")
            self.c = math.sqrt(self.a ** 2 + self.b ** 2)
            if "side" in self.targets:
                result["side_c"] = self._add_step("Знаходимо гіпотенузу (Теорема Піфагора)", "c = √(a² + b²)",
                                                  f"c = √({self.a}² + {self.b}²)", self.c)

        elif self.task_type == "RIGHT_LEG_HYPOTENUSE":
            self._steps.append(f"Фігура: Прямокутний трикутник з катетом a={self.a} і гіпотенузою c={self.c}")
            self.b = math.sqrt(self.c ** 2 - self.a ** 2)
            if "side" in self.targets:
                result["side_b"] = self._add_step("Знаходимо другий катет (Теорема Піфагора)", "b = √(c² - a²)",
                                                  f"b = √({self.c}² - {self.a}²)", self.b)

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу прямокутного трикутника", "S = (a * b) / 2",
                                            f"S = ({self.a:.2f} * {self.b:.2f}) / 2", (self.a * self.b) / 2)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + b + c",
                                                 f"P = {self.a:.2f} + {self.b:.2f} + {self.c:.2f}",
                                                 self.a + self.b + self.c)

        if "incircle" in self.targets:
            r_in = (self.a + self.b - self.c) / 2
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = (a + b - c) / 2",
                                                   f"r = ({self.a:.2f} + {self.b:.2f} - {self.c:.2f}) / 2", r_in)

        if "circumcircle" in self.targets:
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = c / 2",
                                                       f"R = {self.c:.2f} / 2", self.c / 2)

        image_base64 = TrianglePlotter(self.a, self.b, self.c).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
