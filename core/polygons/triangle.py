import math
from core.base import GeometricSolver


class TriangleSSSSolver(GeometricSolver):
    """Розв'язувач трикутника за трьома сторонами (SSS)."""

    def __init__(self, a: float, b: float, c: float, target: str = "all"):
        super().__init__(target)
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0 or self.c <= 0:
            self._steps.append("Помилка: Сторони мають бути додатними.")
            return False
        if (self.a + self.b <= self.c) or (self.a + self.c <= self.b) or (self.b + self.c <= self.a):
            self._steps.append("Помилка: Такий трикутник не існує (сума двох сторін має бути більшою за третю).")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        self._steps.append(f"Дано трикутник: a={self.a}, b={self.b}, c={self.c}")

        # 1. Площа (Формула Герона)
        thm_heron = self.db.get_theorem("Формула Герона")
        p = (self.a + self.b + self.c) / 2
        s = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

        self._steps.append(f"➤ Площа:")
        self._steps.append(f"{thm_heron['description']} ({thm_heron['formula']})")
        self._steps.append(f"Півпериметр p = {p}. Площа S ≈ {s:.2f}")

        # 2. Радіус вписаного кола (r)
        thm_in = self.db.get_theorem("Радіус вписаного кола (трикутник)")
        r_in = s / p
        self._steps.append(f"➤ Вписане коло:")
        self._steps.append(f"{thm_in['description']} ({thm_in['formula']})")
        self._steps.append(f"r = {s:.2f} / {p} ≈ {r_in:.2f}")

        # 3. Радіус описаного кола (R)
        thm_out = self.db.get_theorem("Радіус описаного кола (трикутник)")
        r_out = (self.a * self.b * self.c) / (4 * s)
        self._steps.append(f"➤ Описане коло:")
        self._steps.append(f"{thm_out['description']} ({thm_out['formula']})")
        self._steps.append(f"R = ({self.a}*{self.b}*{self.c}) / (4*{s:.2f}) ≈ {r_out:.2f}")

        return {
            "success": True,
            "data": {
                "perimeter": round(p * 2, 2),
                "area": round(s, 2),
                "r_inscribed": round(r_in, 2),
                "r_circumscribed": round(r_out, 2)
            },
            "steps": self._steps
        }