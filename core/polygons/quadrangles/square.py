import math
from core.base import GeometricSolver
from plotters.rectangle_plotter import RectanglePlotter


class SquareSolver(GeometricSolver):
    """Розв'язувач задач для квадрата."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))

    def validate(self) -> bool:
        if self.a <= 0:
            self._steps.append("Помилка: Сторона квадрата має бути додатною.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Квадрат зі стороною a={self.a}")

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу квадрата", "S = a²", f"S = {self.a}²", self.a ** 2)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = 4 * a", f"P = 4 * {self.a}", 4 * self.a)

        if "diagonal" in self.targets:
            diag = self.a * math.sqrt(2)
            result["diagonal"] = self._add_step("Знаходимо діагональ", "d = a * √2", f"d = {self.a} * √2 ≈", diag)

        if "incircle" in self.targets:
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = a / 2", f"r = {self.a} / 2",
                                                   self.a / 2)

        if "circumcircle" in self.targets:
            diag = self.a * math.sqrt(2)
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = d / 2",
                                                       f"R = {diag:.2f} / 2", diag / 2)

        image_base64 = RectanglePlotter(self.a, self.a).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}