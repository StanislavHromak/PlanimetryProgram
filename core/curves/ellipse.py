import math
from core.base import GeometricSolver
from core.curves.plotters.ellipse_plotter import EllipsePlotter


class EllipseSolver(GeometricSolver):
    """Розв'язувач задач для еліпса."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0:
            self._add_error("Піввісі мають бути додатними.")
            return False
        return True

    def _calculate(self):
        self.step_num = 1
        result = {}

        self._add_info(f"Еліпс: велика піввісь a={self.a}, мала піввісь b={self.b}")

        if self._is_target("area"):
            area = math.pi * self.a * self.b
            result["area"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо площу",
                "S = π · a · b",
                f"S = π · {self.a} · {self.b}",
                area
            )
            self.step_num += 1

        if self._is_target("perimeter"):
            h_numerator = (self.a - self.b) ** 2
            h_denominator = (self.a + self.b) ** 2
            h = h_numerator / h_denominator

            self._add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо допоміжний параметр h для формули Рамануджана",
                "h = (a - b)² / (a + b)²",
                f"h = ({self.a} - {self.b})² / ({self.a} + {self.b})²",
                h,
                is_intermediate=True
            )
            self.step_num += 1

            term = (3 * h) / (10 + math.sqrt(4 - 3 * h))
            perim = math.pi * (self.a + self.b) * (1 + term)

            result["perimeter"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо периметр еліпса",
                "P ≈ π(a + b) · (1 + 3h / (10 + √(4 - 3h)))",
                f"P ≈ π({self.a} + {self.b}) · (1 + (3 · {h:.4f}) / (10 + √(4 - 3 · {h:.4f})))",
                perim,
                rule="Точного значення периметра еліпса не існує у вигляді простої формули. Ми використовуємо високоточне наближення Рамануджана."
            )
            self.step_num += 1

        if self._is_target("eccentricity"):
            major = max(self.a, self.b)
            minor = min(self.a, self.b)
            ecc = math.sqrt(1 - (minor ** 2 / major ** 2))
            result["eccentricity"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо ексцентриситет",
                "e = √(1 - (b/a)²)",
                f"e = √(1 - ({minor}/{major})²)",
                ecc,
                rule="Ексцентриситет показує ступінь 'сплюснутості' еліпса. Він завжди знаходиться в межах від 0 до 1."
            )
            self.step_num += 1

        image_base64 = EllipsePlotter(self.a, self.b).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}