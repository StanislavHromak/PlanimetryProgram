import math
from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class IsoscelesTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівнобедреного трикутника."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.base = float(params.get('base', 0))  # основа (a)
        self.side = float(params.get('side', 0))  # бічна сторона (b = c)

    def validate(self) -> bool:
        if self.base <= 0 or self.side <= 0:
            self._add_error("Сторони мають бути додатними.")
            return False
        if self.base >= 2 * self.side:
            self._add_error(
                "Основа має бути меншою за подвоєну бічну сторону (нерівність трикутника)."
            )
            return False
        return True

    def _compute_height(self) -> float:
        """Висота до основи. Проміжна — якщо 'area' не в targets."""
        if 'h' in self._computed:
            return self._computed['h']

        value = math.sqrt(self.side ** 2 - (self.base / 2) ** 2)

        if not self._is_target("area"):
            self._add_step(
                "Знаходимо висоту до основи (проміжне)",
                "h = √(b² - (a/2)²)",
                f"h = √({self.side}² - ({self.base}/2)²)",
                value,
                rule="Висота рівнобедреного трикутника, опущена на основу, ділить її навпіл "
                     "і є перпендикуляром: h = √(b² - (a/2)²).",
                is_intermediate=True
            )

        self._computed['h'] = value
        return value

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]["text"]}

        result = {}
        step_num = 1

        self._add_info(
            f"Рівнобедрений трикутник: основа a={self.base}, бічна сторона b={self.side}"
        )

        # Крок 1 — площа (залежить від висоти h)
        if self._is_target("area"):
            h = self._compute_height()
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо висоту до основи",
                "h = √(b² - (a/2)²)",
                f"h = √({self.side}² - ({self.base}/2)²)",
                h,
                rule="Висота рівнобедреного трикутника, опущена на основу, ділить її навпіл "
                     "і є перпендикуляром: h = √(b² - (a/2)²).",
            )
            step_num += 1

            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу",
                "S = (a · h) / 2",
                f"S = ({self.base} · {h:.2f}) / 2",
                (self.base * h) / 2,
                rule="Площа трикутника через основу і висоту: S = (a · h) / 2."
            )
            step_num += 1

        # Крок 2 — периметр (не потребує проміжних)
        if self._is_target("perimeter"):
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = a + 2·b",
                f"P = {self.base} + 2·{self.side}",
                self.base + 2 * self.side,
                rule="Периметр рівнобедреного трикутника: P = a + 2b, "
                     "де a — основа, b — бічна сторона."
            )

        image_base64 = TrianglePlotter(self.base, self.side, self.side).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
