import math
from core.base import GeometricSolver
from core.plotter import GeometryPlotter


class TriangleSSSSolver(GeometricSolver):
    """Розв'язувач трикутника за трьома сторонами (SSS)."""

    def __init__(self, a: float, b: float, c: float, targets: list = None):
        super().__init__(targets)
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
        result_data = {}

        # --- БАЗОВА МАТЕМАТИКА ---
        p = (self.a + self.b + self.c) / 2
        area = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))
        r_in = area / p
        r_out = (self.a * self.b * self.c) / (4 * area)

        # Знаходимо кути в радіанах, а потім переводимо в градуси
        cos_alpha = (self.b ** 2 + self.c ** 2 - self.a ** 2) / (2 * self.b * self.c)
        cos_beta = (self.a ** 2 + self.c ** 2 - self.b ** 2) / (2 * self.a * self.c)

        # Захист від похибок (щоб косинус не виліз за межі [-1, 1])
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        cos_beta = max(-1.0, min(1.0, cos_beta))

        angle_a = math.degrees(math.acos(cos_alpha))
        angle_b = math.degrees(math.acos(cos_beta))
        angle_c = 180.0 - angle_a - angle_b

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ЗАПИТОМ ---
        if "side" in self.targets:
            thm = self.db.get_theorem("Теорема косинусів")
            self._steps.append(f"➤ Знаходимо невідомі кути:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(
                f"cos(α) = (b² + c² - a²) / 2bc = ({self.b}² + {self.c}² - {self.a}²) / (2*{self.b}*{self.c})")
            self._steps.append(f"α ≈ {angle_a:.2f}°")
            self._steps.append(
                f"cos(β) = (a² + c² - b²) / 2ac = ({self.a}² + {self.c}² - {self.b}²) / (2*{self.a}*{self.c})")
            self._steps.append(f"β ≈ {angle_b:.2f}°")
            self._steps.append(f"γ = 180° - α - β ≈ {angle_c:.2f}°")

            result_data["angle_a"] = round(angle_a, 2)
            result_data["angle_b"] = round(angle_b, 2)
            result_data["angle_c"] = round(angle_c, 2)

        if "perimeter" in self.targets:
            self._steps.append(f"➤ Периметр:")
            self._steps.append(f"P = a + b + c = {self.a} + {self.b} + {self.c} = {p * 2}")
            result_data["perimeter"] = round(p * 2, 2)

        if "area" in self.targets:
            thm = self.db.get_theorem("Формула Герона")
            self._steps.append(f"➤ Площа:")
            self._steps.append(f"{thm['description']} ({thm['formula']})")
            self._steps.append(f"S ≈ {area:.2f}")
            result_data["area"] = round(area, 2)

        if "incircle" in self.targets:
            thm = self.db.get_theorem("Радіус вписаного кола (трикутник)")
            self._steps.append(f"➤ Вписане коло:")
            self._steps.append(f"{thm['description']} ({thm['formula']})")
            self._steps.append(f"r = S / p ≈ {area:.2f} / {p:.2f} ≈ {r_in:.2f}")
            result_data["r_inscribed"] = round(r_in, 2)

        if "circumcircle" in self.targets:
            thm = self.db.get_theorem("Радіус описаного кола (трикутник)")
            self._steps.append(f"➤ Описане коло:")
            self._steps.append(f"{thm['description']} ({thm['formula']})")
            self._steps.append(f"R = ({self.a}*{self.b}*{self.c}) / (4*{area:.2f}) ≈ {r_out:.2f}")
            result_data["r_circumscribed"] = round(r_out, 2)

        # Малюємо креслення
        image_base64 = GeometryPlotter.plot_triangle(self.a, self.b, self.c)

        return {
            "success": True,
            "data": result_data,
            "steps": self._steps,
            "image": image_base64
        }


class TriangleSASSolver(GeometricSolver):
    """Розв'язувач трикутника за двома сторонами і кутом між ними (SAS)."""

    def __init__(self, a: float, b: float, angle_c: float, targets: list = None):
        super().__init__(targets)
        self.a = float(a)
        self.b = float(b)
        self.angle_c = float(angle_c)

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
        result_data = {}

        # --- БАЗОВА МАТЕМАТИКА (Рахуємо все тихо) ---
        rad_c = math.radians(self.angle_c)
        c = math.sqrt(self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad_c))

        perim = self.a + self.b + c
        p = perim / 2
        area = 0.5 * self.a * self.b * math.sin(rad_c)

        r_in = area / p
        r_out = c / (2 * math.sin(rad_c))  # Оптимізація через наслідок теореми синусів

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ЗАПИТОМ ---
        if "side" in self.targets:
            thm = self.db.get_theorem("Теорема косинусів")
            self._steps.append(f"➤ Знаходимо невідому сторону c:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"c ≈ {c:.2f}")
            result_data["side_c"] = round(c, 2)
        else:
            self._steps.append(f"ℹ️ Для подальших розрахунків визначаємо сторону c ≈ {c:.2f}")

        if "perimeter" in self.targets:
            self._steps.append(f"➤ Периметр: P ≈ {perim:.2f}")
            result_data["perimeter"] = round(perim, 2)

        if "area" in self.targets:
            self._steps.append(f"➤ Знаходимо площу:")
            self._steps.append(f"S = 1/2 * a * b * sin(γ) ≈ {area:.2f}")
            result_data["area"] = round(area, 2)

        if "incircle" in self.targets:
            thm = self.db.get_theorem("Радіус вписаного кола (трикутник)")
            self._steps.append(f"➤ Вписане коло:")
            self._steps.append(f"{thm['description']} ({thm['formula']})")
            self._steps.append(f"r = S / p ≈ {area:.2f} / {p:.2f} ≈ {r_in:.2f}")
            result_data["r_inscribed"] = round(r_in, 2)

        if "circumcircle" in self.targets:
            self._steps.append(f"➤ Описане коло (наслідок теореми синусів):")
            self._steps.append(f"R = c / (2 * sin(γ)) ≈ {c:.2f} / (2 * {math.sin(rad_c):.2f}) ≈ {r_out:.2f}")
            result_data["r_circumscribed"] = round(r_out, 2)

        image_base64 = GeometryPlotter.plot_triangle(self.a, self.b, c)

        return {
            "success": True,
            "data": result_data,
            "steps": self._steps,
            "image": image_base64
        }


class TriangleASASolver(GeometricSolver):
    """Розв'язувач трикутника за стороною та двома прилеглими кутами (ASA)."""

    def __init__(self, a: float, angle_b: float, angle_c: float, targets: list = None):
        super().__init__(targets)
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
        result_data = {}

        # --- БАЗОВА МАТЕМАТИКА (Рахуємо все тихо) ---
        angle_a = 180 - self.angle_b - self.angle_c
        rad_a = math.radians(angle_a)
        rad_b = math.radians(self.angle_b)
        rad_c = math.radians(self.angle_c)

        b = (self.a * math.sin(rad_b)) / math.sin(rad_a)
        c = (self.a * math.sin(rad_c)) / math.sin(rad_a)

        perim = self.a + b + c
        p = perim / 2
        area = 0.5 * b * c * math.sin(rad_a)

        r_in = area / p
        r_out = self.a / (2 * math.sin(rad_a))

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ЗАПИТОМ ---
        if "side" in self.targets:
            thm_sin = self.db.get_theorem("Теорема синусів")
            self._steps.append(f"➤ Знаходимо третій кут та невідомі сторони:")
            self._steps.append(f"α = 180° - {self.angle_b}° - {self.angle_c}° = {angle_a}°")
            self._steps.append(f"Правило: {thm_sin['description']}")
            self._steps.append(f"b = ({self.a} * sin({self.angle_b}°)) / sin({angle_a}°) ≈ {b:.2f}")
            self._steps.append(f"c = ({self.a} * sin({self.angle_c}°)) / sin({angle_a}°) ≈ {c:.2f}")

            result_data["angle_a"] = round(angle_a, 2)
            result_data["side_b"] = round(b, 2)
            result_data["side_c"] = round(c, 2)
        else:
            self._steps.append(f"ℹ️ Для подальших розрахунків визначаємо: α={angle_a}°, b≈{b:.2f}, c≈{c:.2f}")

        if "perimeter" in self.targets:
            self._steps.append(f"➤ Периметр: P = a + b + c ≈ {perim:.2f}")
            result_data["perimeter"] = round(perim, 2)

        if "area" in self.targets:
            self._steps.append(f"➤ Площа:")
            self._steps.append(f"S = 1/2 * b * c * sin(α) ≈ {area:.2f}")
            result_data["area"] = round(area, 2)

        if "incircle" in self.targets:
            thm_in = self.db.get_theorem("Радіус вписаного кола (трикутник)")
            self._steps.append(f"➤ Вписане коло:")
            self._steps.append(f"{thm_in['description']} ({thm_in['formula']})")
            self._steps.append(f"r = S / p ≈ {area:.2f} / {p:.2f} ≈ {r_in:.2f}")
            result_data["r_inscribed"] = round(r_in, 2)

        if "circumcircle" in self.targets:
            self._steps.append(f"➤ Описане коло (за наслідком теореми синусів):")
            self._steps.append(f"R = a / (2 * sin(α)) ≈ {self.a} / (2 * {math.sin(rad_a):.2f}) ≈ {r_out:.2f}")
            result_data["r_circumscribed"] = round(r_out, 2)

        image_base64 = GeometryPlotter.plot_triangle(self.a, b, c)

        return {
            "success": True,
            "data": result_data,
            "steps": self._steps,
            "image": image_base64
        }