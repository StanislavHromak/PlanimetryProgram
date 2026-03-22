import math
from core.base import GeometricSolver
from .plotters.ellipse_plotter import EllipsePlotter


class EllipseSolver(GeometricSolver):
    """Розв'язувач задач для еліпса."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type  # Зберігаємо тип задачі
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0:
            self._steps.append("Помилка: Піввісі мають бути додатними.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}

        # Тепер використовуємо task_type для опису початку задачі
        if self.task_type == "ELLIPSE_AXES":
            self._steps.append(f"Фігура: Еліпс із великою піввіссю a={self.a} та малою b={self.b}")

        if "area" in self.targets:
            area = math.pi * self.a * self.b
            result["area"] = self._add_step("Площа еліпса", "S = π * a * b",
                                            f"S = π * {self.a} * {self.b}", area)

        if "perimeter" in self.targets:
            # Наближена формула Рамануджана
            h = ((self.a - self.b) ** 2) / ((self.a + self.b) ** 2)
            perim = math.pi * (self.a + self.b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
            result["perimeter"] = self._add_step("Периметр (наближено)",
                                                 "P ≈ π(a+b)(1 + 3h/(10+√(4-3h)))",
                                                 "Використано формулу Рамануджана", perim)

        if "eccentricity" in self.targets:
            major = max(self.a, self.b)
            minor = min(self.a, self.b)
            ecc = math.sqrt(1 - (minor ** 2 / major ** 2))
            result["eccentricity"] = self._add_step("Ексцентриситет", "e = √(1 - b²/a²)",
                                                    f"e = √(1 - {minor}²/{major}²)", ecc)

        return {
            "success": True,
            "data": result,
            "steps": self._steps,
            "image": EllipsePlotter(self.a, self.b).plot()
        }