import math
from core.base import GeometricSolver
from plotters.arbitary_quadrangle_plotter import ArbitraryQuadranglePlotter


class ArbitraryQuadrangleSolver(GeometricSolver):
    """Розв'язувач задач з довільним чотирикутником."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.c = float(params.get('c', 0))
        self.d = float(params.get('d', 0))
        self.angle = float(params.get('angle', 0))
        self.D = 0.0

    def validate(self) -> bool:
        if any(v <= 0 for v in [self.a, self.b, self.c, self.d]):
            self._steps.append("Помилка: Всі сторони мають бути додатними.")
            return False
        if self.angle <= 0 or self.angle >= 180:
            self._steps.append("Помилка: Кут має бути в межах від 0° до 180°.")
            return False

        rad = math.radians(self.angle)
        self.D = math.sqrt(self.a ** 2 + self.d ** 2 - 2 * self.a * self.d * math.cos(rad))
        if (self.b + self.c <= self.D) or (self.b + self.D <= self.c) or (self.c + self.D <= self.b):
            self._steps.append(
                "Помилка: Такий чотирикутник не існує. Сторони не зійдуться (порушена нерівність трикутника).")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(
            f"Фігура: Довільний чотирикутник (a={self.a}, b={self.b}, c={self.c}, d={self.d}, α={self.angle}°)")

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + b + c + d",
                                                 f"P = {self.a} + {self.b} + {self.c} + {self.d}",
                                                 self.a + self.b + self.c + self.d)

        if "area" in self.targets:
            rad = math.radians(self.angle)
            s1 = 0.5 * self.a * self.d * math.sin(rad)
            p2 = (self.b + self.c + self.D) / 2
            s2 = math.sqrt(p2 * (p2 - self.b) * (p2 - self.c) * (p2 - self.D))

            self._steps.append("➤ Знаходимо площу:")
            self._steps.append("Правило: Площа дорівнює сумі площ двох трикутників, на які фігуру розбиває діагональ.")
            self._steps.append(f"Проміжний крок: Діагональ D ≈ {self.D:.2f}, S1 ≈ {s1:.2f}, S2 ≈ {s2:.2f}")
            # Використовуємо порожній рядок "" замість None
            result["area"] = self._add_step("", "S = S1 + S2", f"S = {s1:.2f} + {s2:.2f}", s1 + s2)

        if "circles_check" in self.targets:
            self._steps.append("➤ Перевірка на можливість вписати/описати коло:")
            if math.isclose(self.a + self.c, self.b + self.d, rel_tol=1e-3):
                self._steps.append("✅ <b>Вписане коло:</b> ІСНУЄ (сума a+c дорівнює b+d).")
                result["can_inscribe"] = "Так"
            else:
                self._steps.append("❌ <b>Вписане коло:</b> НЕ ІСНУЄ (a+c ≠ b+d).")
                result["can_inscribe"] = "Ні"

            cos_opp = (self.b ** 2 + self.c ** 2 - self.D ** 2) / (2 * self.b * self.c)
            opp_angle = math.degrees(math.acos(max(-1.0, min(1.0, cos_opp))))
            if math.isclose(self.angle + opp_angle, 180.0, rel_tol=1e-3):
                self._steps.append("✅ <b>Описане коло:</b> ІСНУЄ (сума протилежних кутів дорівнює 180°).")
                result["can_circumscribe"] = "Так"
            else:
                self._steps.append("❌ <b>Описане коло:</b> НЕ ІСНУЄ (сума протилежних кутів ≠ 180°).")
                result["can_circumscribe"] = "Ні"

        # Координати для плоттера
        rad = math.radians(self.angle)
        v4 = (self.d * math.cos(rad), self.d * math.sin(rad))
        theta = math.atan2(v4[1], v4[0] - self.a)
        cos_beta = (self.b ** 2 + self.D ** 2 - self.c ** 2) / (2 * self.b * self.D)
        beta = math.acos(max(-1.0, min(1.0, cos_beta)))
        v3 = (self.a + self.b * math.cos(theta - beta), self.b * math.sin(theta - beta))

        plotter = ArbitraryQuadranglePlotter([(0, 0), (self.a, 0), v3, v4], self.a, self.b, self.c, self.d, self.angle)
        image_base64 = plotter.plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}