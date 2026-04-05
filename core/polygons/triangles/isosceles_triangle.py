import math
from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class IsoscelesTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівнобедреного трикутника."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.base = float(params.get('base', 0))
        self.side = float(params.get('side', 0))

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
        """Тихо обчислює висоту до основи (без виведення кроків)."""
        if 'h' in self._computed:
            return self._computed['h']

        value = math.sqrt(self.side ** 2 - (self.base / 2) ** 2)
        self._computed['h'] = value
        return value

    def _calculate(self):
        self.step_num = 1
        result = {}

        self._add_info(f"Рівнобедрений трикутник: основа a={self.base}, бічна сторона b={self.side}")

        needs_height = self._is_target("height") or self._is_target("area")

        if needs_height:
            h = self._compute_height()
            is_int = not self._is_target("height")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_height" if is_int else "height"

            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо висоту до основи",
                "h = √(b² - (a/2)²)",
                f"h = √({self.side}² - ({self.base}/2)²)",
                h,
                rule="Висота рівнобедреного трикутника, опущена на основу, ділить її навпіл "
                     "і є перпендикуляром: h = √(b² - (a/2)²).",
                is_intermediate=is_int
            )
            self.step_num += 1

        if self._is_target("area"):
            h = self._compute_height()
            result["area"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо площу",
                "S = (a · h) / 2",
                f"S = ({self.base} · {h:.2f}) / 2",
                (self.base * h) / 2,
                rule="Площа трикутника через основу і висоту: S = (a · h) / 2."
            )
            self.step_num += 1

        if self._is_target("perimeter"):
            result["perimeter"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо периметр",
                "P = a + 2·b",
                f"P = {self.base} + 2·{self.side}",
                self.base + 2 * self.side,
                rule="Периметр рівнобедреного трикутника: P = a + 2b, де a — основа, b — бічна сторона."
            )
            self.step_num += 1

        image_base64 = TrianglePlotter(self.base, self.side, self.side).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
