import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rectangle_plotter import RectanglePlotter


class RectangleSolver(GeometricSolver):
    """Розв'язувач задач з прямокутником."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0:
            self._steps.append("Помилка: Сторони прямокутника мають бути додатними.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Прямокутник зі сторонами a={self.a}, b={self.b}")

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу прямокутника", "S = a * b", f"S = {self.a} * {self.b}",
                                            self.a * self.b)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = 2 * (a + b)",
                                                 f"P = 2 * ({self.a} + {self.b})", 2 * (self.a + self.b))

        diag = math.sqrt(self.a ** 2 + self.b ** 2)
        if "diagonal" in self.targets:
            result["diagonal"] = self._add_step("Знаходимо діагональ", "d = √(a² + b²)",
                                                f"d = √({self.a}² + {self.b}²) ≈", diag)

        if "circumcircle" in self.targets:
            self._steps.append("➤ Знаходимо радіус описаного кола:")
            self._steps.append("Правило: Центр описаного кола лежить на перетині діагоналей.")
            # Використовуємо порожній рядок "" замість None
            result["r_circumscribed"] = self._add_step("", "R = d / 2", f"R = {diag:.2f} / 2", diag / 2)

        image_base64 = RectanglePlotter(self.a, self.b).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}