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

        if self.task_type == "ELLIPSE_AXES":
            self._steps.append(f"Фігура: Еліпс із великою піввіссю a={self.a} та малою b={self.b}")

        # --- ПЛОЩА ---
        if "area" in self.targets:
            area = math.pi * self.a * self.b
            result["area"] = self._add_step("Площа еліпса", "S = π * a * b",
                                            f"S = π * {self.a} * {self.b}", area)

        # --- ПЕРИМЕТР (З ПРОМІЖНИМ КРОКОМ) ---
        if "perimeter" in self.targets:
            # 1. Рахуємо допоміжний параметр h
            h_numerator = (self.a - self.b) ** 2
            h_denominator = (self.a + self.b) ** 2
            h = h_numerator / h_denominator

            self._steps.append("➤ Знаходимо допоміжний параметр h для формули Рамануджана:")
            self._steps.append(f"Формула: h = (a - b)² / (a + b)²")
            self._steps.append(
                f"Розв'язок: h = ({self.a} - {self.b})² / ({self.a} + {self.b})² = <span style='color: red; font-weight: bold;'>{h:.6f}</span>")

            # 2. Рахуємо периметр
            term = (3 * h) / (10 + math.sqrt(4 - 3 * h))
            perim = math.pi * (self.a + self.b) * (1 + term)

            result["perimeter"] = self._add_step(
                "Периметр еліпса (наближення Рамануджана)",
                "P ≈ π(a + b) * (1 + 3h / (10 + √(4 - 3h)))",
                f"P ≈ π({self.a} + {self.b}) * (1 + (3 * {h:.4f}) / (10 + √(4 - 3 * {h:.4f})))",
                perim
            )

        # --- ЕКСЦЕНТРИСИТЕТ ---
        if "eccentricity" in self.targets:
            major = max(self.a, self.b)
            minor = min(self.a, self.b)
            ecc = math.sqrt(1 - (minor ** 2 / major ** 2))
            result["eccentricity"] = self._add_step("Ексцентриситет", "e = √(1 - (b/a)²)",
                                                    f"e = √(1 - ({minor}/{major})²)", ecc)

        return {
            "success": True,
            "data": result,
            "steps": self._steps,
            "image": EllipsePlotter(self.a, self.b).plot()
        }