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


class TriangleSASSolver(GeometricSolver):
    """Розв'язувач трикутника за двома сторонами та кутом між ними (SAS)."""

    def __init__(self, a: float, b: float, angle_c: float, target: str = "all"):
        super().__init__(target)
        self.a = float(a)
        self.b = float(b)
        self.angle_c = float(angle_c)  # Кут в градусах

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0:
            self._steps.append("Помилка: Сторони мають бути додатними.")
            return False
        if self.angle_c <= 0 or self.angle_c >= 180:
            self._steps.append("Помилка: Кут має бути в межах від 0 до 180 градусів.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        self._steps.append(f"Дано: a={self.a}, b={self.b}, Кут γ={self.angle_c}°")

        # 1. Шукаємо третю сторону за теоремою косинусів
        thm_cos = self.db.get_theorem("Теорема косинусів")
        angle_c_rad = math.radians(self.angle_c)

        c_sq = self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(angle_c_rad)
        c = math.sqrt(c_sq)

        self._steps.append(f"➤ Знаходимо невідому сторону c:")
        self._steps.append(f"Правило: {thm_cos['description']}")
        self._steps.append(
            f"Підстановка: c = √({self.a}² + {self.b}² - 2*{self.a}*{self.b}*cos({self.angle_c}°)) ≈ {c:.2f}")

        # 2. Шукаємо площу (через синус)
        area = 0.5 * self.a * self.b * math.sin(angle_c_rad)
        self._steps.append(f"➤ Знаходимо площу:")
        self._steps.append(f"Формула: S = 1/2 * a * b * sin(γ)")
        self._steps.append(f"Обчислення: S = 0.5 * {self.a} * {self.b} * sin({self.angle_c}°) ≈ {area:.2f}")

        return {
            "success": True,
            "data": {
                "side_c": round(c, 2),
                "area": round(area, 2),
                "perimeter": round(self.a + self.b + c, 2)
            },
            "steps": self._steps
        }


class TriangleASASolver(GeometricSolver):
    """Розв'язувач трикутника за стороною та двома прилеглими кутами (ASA)."""

    def __init__(self, a: float, angle_b: float, angle_c: float, target: str = "all"):
        super().__init__(target)
        self.a = float(a)
        self.angle_b = float(angle_b)
        self.angle_c = float(angle_c)

    def validate(self) -> bool:
        if self.a <= 0:
            self._steps.append("Помилка: Сторона має бути додатним числом.")
            return False
        if self.angle_b <= 0 or self.angle_c <= 0:
            self._steps.append("Помилка: Кути мають бути додатними.")
            return False
        if self.angle_b + self.angle_c >= 180:
            self._steps.append("Помилка: Сума двох кутів має бути меншою за 180 градусів.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        self._steps.append(f"Дано: сторона a={self.a}, прилеглі кути β={self.angle_b}°, γ={self.angle_c}°")

        # 1. Знаходимо третій кут
        angle_a = 180 - self.angle_b - self.angle_c
        self._steps.append(f"➤ Знаходимо третій кут (α):")
        self._steps.append(f"Сума кутів трикутника дорівнює 180°.")
        self._steps.append(f"α = 180° - {self.angle_b}° - {self.angle_c}° = {angle_a}°")

        # 2. Знаходимо інші сторони за теоремою синусів
        thm_sin = self.db.get_theorem("Теорема синусів")
        rad_a = math.radians(angle_a)
        rad_b = math.radians(self.angle_b)
        rad_c = math.radians(self.angle_c)

        b = (self.a * math.sin(rad_b)) / math.sin(rad_a)
        c = (self.a * math.sin(rad_c)) / math.sin(rad_a)

        self._steps.append(f"➤ Знаходимо сторони b та c:")
        self._steps.append(f"Правило: {thm_sin['description']}")
        self._steps.append(f"b = ({self.a} * sin({self.angle_b}°)) / sin({angle_a}°) ≈ {b:.2f}")
        self._steps.append(f"c = ({self.a} * sin({self.angle_c}°)) / sin({angle_a}°) ≈ {c:.2f}")

        # 3. Площа
        area = 0.5 * b * c * math.sin(rad_a)

        return {
            "success": True,
            "data": {
                "angle_a": round(angle_a, 2),
                "side_b": round(b, 2),
                "side_c": round(c, 2),
                "area": round(area, 2),
                "perimeter": round(self.a + b + c, 2)
            },
            "steps": self._steps
        }