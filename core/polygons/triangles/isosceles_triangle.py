import math
from core.base import GeometricSolver
from plotters.triangle_plotter import TrianglePlotter


class IsoscelesTriangleSolver(GeometricSolver):
    """
    Розв'язувач задач для рівнобедреного трикутника.
    """

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.base = float(params.get('base', 0))  # основа (a)
        self.side = float(params.get('side', 0))  # бічна сторона (b = c)

    def validate(self) -> bool:
        if self.task_type == "ISOSCELES_BASE_SIDE":
            if self.base <= 0 or self.side <= 0:
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
            if self.base >= 2 * self.side:
                self._steps.append("Помилка: Основа має бути меншою за подвоєну бічну сторону (нерівність трикутника).")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Рівнобедрений трикутник з основою a={self.base} та бічною стороною b={self.side}")

        # Висота до основи
        h = math.sqrt(self.side ** 2 - (self.base / 2) ** 2)

        if "area" in self.targets:
            area = (self.base * h) / 2
            self._add_step("", "h = √(b² - (a/2)²)", f"h = √({self.side}² - ({self.base}/2)²) ≈", h)
            result["area"] = self._add_step("Знаходимо площу", "S = (a * h) / 2", f"S = ({self.base} * {h:.2f}) / 2",
                                            area)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + 2b", f"P = {self.base} + 2*{self.side}",
                                                 self.base + 2 * self.side)

        image_base64 = TrianglePlotter(self.base, self.side, self.side).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
