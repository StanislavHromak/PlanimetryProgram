import math
from core.base import GeometricSolver
from plotters.parallelogram_plotter import ParallelogramPlotter


class ParallelogramSolver(GeometricSolver):
    """Розв'язувач задач з паралелограмом."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.d1 = float(params.get('d1', 0))
        self.d2 = float(params.get('d2', 0))
        self.angle = float(params.get('angle', 0))

    def validate(self) -> bool:
        if self.task_type == "PARALLELOGRAM_S_A":
            if self.a <= 0 or self.b <= 0:
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
        elif self.task_type == "PARALLELOGRAM_D_A":
            if self.d1 <= 0 or self.d2 <= 0:
                self._steps.append("Помилка: Діагоналі мають бути додатними.")
                return False
        if self.angle <= 0 or self.angle >= 180:
            self._steps.append("Помилка: Кут має бути в межах від 0° до 180°.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None

        if self.task_type == "PARALLELOGRAM_S_A":
            self._steps.append(f"Фігура: Паралелограм зі сторонами a={self.a}, b={self.b} і кутом {self.angle}°")
            if "area" in self.targets:
                area = self.a * self.b * math.sin(math.radians(self.angle))
                result["area"] = self._add_step("Знаходимо площу", "S = a * b * sin(α)",
                                                f"S = {self.a} * {self.b} * sin({self.angle}°)", area)
            if "perimeter" in self.targets:
                result["perimeter"] = self._add_step("Знаходимо периметр", "P = 2 * (a + b)",
                                                     f"P = 2 * ({self.a} + {self.b})", 2 * (self.a + self.b))
            image_base64 = ParallelogramPlotter(self.a, self.a, self.angle).plot()

        elif self.task_type == "PARALLELOGRAM_D_A":
            self._steps.append(
                f"Фігура: Паралелограм з діагоналями d1={self.d1}, d2={self.d2} і кутом між ними γ={self.angle}°")
            if "area" in self.targets:
                area = 0.5 * self.d1 * self.d2 * math.sin(math.radians(self.angle))
                result["area"] = self._add_step("Знаходимо площу через діагоналі", "S = 1/2 * d1 * d2 * sin(γ)",
                                                f"S = 0.5 * {self.d1} * {self.d2} * sin({self.angle}°)", area)

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}