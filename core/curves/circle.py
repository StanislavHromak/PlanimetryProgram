import math
from core.base import GeometricSolver


class CircleSolver(GeometricSolver):
    """Розв'язувач задач для кола та круга."""

    def __init__(self, radius: float, target: str = "all"):
        super().__init__(target)
        self.r = float(radius)

    def validate(self) -> bool:
        if self.r <= 0:
            self._steps.append("Помилка: Радіус має бути додатним числом.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        self._steps.append(f"Дано: Коло з радіусом r = {self.r}")

        # 1. Довжина кола
        thm_c = self.db.get_theorem("Довжина кола")
        c = 2 * math.pi * self.r
        self._steps.append(f"➤ Знаходимо довжину кола:")
        self._steps.append(f"Правило: {thm_c['description']}")
        self._steps.append(f"Формула: {thm_c['formula']}")
        self._steps.append(f"Обчислення: C = 2 * π * {self.r} ≈ {c:.2f}")

        # 2. Площа круга
        thm_s = self.db.get_theorem("Площа круга")
        s = math.pi * (self.r ** 2)
        self._steps.append(f"➤ Знаходимо площу круга:")
        self._steps.append(f"Правило: {thm_s['description']}")
        self._steps.append(f"Формула: {thm_s['formula']}")
        self._steps.append(f"Обчислення: S = π * {self.r}² ≈ {s:.2f}")

        return {
            "success": True,
            "data": {
                "radius": round(self.r, 2),
                "circumference": round(c, 2),
                "area": round(s, 2)
            },
            "steps": self._steps
        }