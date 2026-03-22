import math
from core.base import GeometricSolver
from core.plotter import TrianglePlotter


class EquilateralTriangleSolver(GeometricSolver):
    """
    Рівносторонній трикутник (правильний).
    Найпростіші формули.
    """

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))

    def validate(self) -> bool:
        if self.a <= 0:
            self._steps.append("Помилка: Сторона має бути додатною.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Рівносторонній трикутник зі стороною a={self.a}")

        if "area" in self.targets:
            area = (self.a ** 2 * math.sqrt(3)) / 4
            result["area"] = self._add_step("Знаходимо площу", "S = (a²√3) / 4", f"S = ({self.a}²√3) / 4", area)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = 3 * a", f"P = 3 * {self.a}", 3 * self.a)

        if "incircle" in self.targets:
            r_in = (self.a * math.sqrt(3)) / 6
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = a√3 / 6",
                                                   f"r = {self.a}√3 / 6", r_in)

        if "circumcircle" in self.targets:
            r_out = (self.a * math.sqrt(3)) / 3
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = a√3 / 3",
                                                       f"R = {self.a}√3 / 3", r_out)

        image_base64 = TrianglePlotter(self.a, self.a, self.a).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}