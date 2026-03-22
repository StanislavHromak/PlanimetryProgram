from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.trapezoid_plotter import TrapezoidPlotter


class TrapezoidSolver(GeometricSolver):
    """Розв'язувач задач для трапеції."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.h = float(params.get('h', 0))

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0 or self.h <= 0:
            self._steps.append("Помилка: Основи та висота мають бути додатними.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Дано: Трапеція з основами a={self.a}, b={self.b} та висотою h={self.h}")

        if "area" in self.targets:
            area = ((self.a + self.b) / 2) * self.h
            result["area"] = self._add_step("Знаходимо площу трапеції", "S = ((a + b) / 2) * h",
                                            f"S = (({self.a} + {self.b}) / 2) * {self.h}", area)

        image_base64 = TrapezoidPlotter(self.a, self.b, self.h).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}