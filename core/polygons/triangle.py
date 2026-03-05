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
        perim = self.a + self.b + self.c
        p = perim / 2
        area = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))
        r_in = area / p
        r_out = (self.a * self.b * self.c) / (4 * area)

        cos_alpha = max(-1.0, min(1.0, (self.b ** 2 + self.c ** 2 - self.a ** 2) / (2 * self.b * self.c)))
        cos_beta = max(-1.0, min(1.0, (self.a ** 2 + self.c ** 2 - self.b ** 2) / (2 * self.a * self.c)))

        angle_a = math.degrees(math.acos(cos_alpha))
        angle_b = math.degrees(math.acos(cos_beta))
        angle_c = 180.0 - angle_a - angle_b

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ШАБЛОНОМ ---
        if "side" in self.targets:
            thm = self.db.get_theorem("Теорема косинусів")
            self._steps.append(f"➤ Знаходимо невідомі кути:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: α = arccos((b² + c² - a²) / 2bc)")
            self._steps.append(
                f"Розв'язок: α = arccos(({self.b}² + {self.c}² - {self.a}²) / (2*{self.b}*{self.c})) = <span style='color: red; font-weight: bold;'>{angle_a:.2f}°</span>")

            self._steps.append(f"Формула: β = arccos((a² + c² - b²) / 2ac)")
            self._steps.append(
                f"Розв'язок: β = arccos(({self.a}² + {self.c}² - {self.b}²) / (2*{self.a}*{self.c})) = <span style='color: red; font-weight: bold;'>{angle_b:.2f}°</span>")

            self._steps.append(f"Формула: γ = 180° - α - β")
            self._steps.append(
                f"Розв'язок: γ = 180° - {angle_a:.2f}° - {angle_b:.2f}° = <span style='color: red; font-weight: bold;'>{angle_c:.2f}°</span>")

            result_data.update(
                {"angle_a": round(angle_a, 2), "angle_b": round(angle_b, 2), "angle_c": round(angle_c, 2)})

        if "perimeter" in self.targets:
            self._steps.append(f"➤ Знаходимо периметр:")
            self._steps.append(f"Формула: P = a + b + c")
            self._steps.append(
                f"Розв'язок: P = {self.a} + {self.b} + {self.c} = <span style='color: red; font-weight: bold;'>{perim:.2f}</span>")
            result_data["perimeter"] = round(perim, 2)

        if "area" in self.targets:
            thm = self.db.get_theorem("Формула Герона")
            self._steps.append(f"➤ Знаходимо площу:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: S = √(p * (p-a) * (p-b) * (p-c))")
            self._steps.append(f"Проміжне значення: півпериметр p = {perim:.2f} / 2 = {p:.2f}")
            self._steps.append(
                f"Розв'язок: S = √({p:.2f} * ({p:.2f}-{self.a}) * ({p:.2f}-{self.b}) * ({p:.2f}-{self.c})) = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
            result_data["area"] = round(area, 2)

        if "incircle" in self.targets:
            thm = self.db.get_theorem("Радіус вписаного кола (трикутник)")
            self._steps.append(f"➤ Знаходимо радіус вписаного кола:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: r = S / p")
            self._steps.append(
                f"Розв'язок: r = {area:.2f} / {p:.2f} = <span style='color: red; font-weight: bold;'>{r_in:.2f}</span>")
            result_data["r_inscribed"] = round(r_in, 2)

        if "circumcircle" in self.targets:
            thm = self.db.get_theorem("Радіус описаного кола (трикутник)")
            self._steps.append(f"➤ Знаходимо радіус описаного кола:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: R = (a*b*c) / (4*S)")
            self._steps.append(
                f"Розв'язок: R = ({self.a}*{self.b}*{self.c}) / (4*{area:.2f}) = <span style='color: red; font-weight: bold;'>{r_out:.2f}</span>")
            result_data["r_circumscribed"] = round(r_out, 2)

        image_base64 = GeometryPlotter.plot_triangle(self.a, self.b, self.c)

        return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}


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

        # --- БАЗОВА МАТЕМАТИКА  ---
        rad_c = math.radians(self.angle_c)
        c = math.sqrt(self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad_c))

        perim = self.a + self.b + c
        p = perim / 2
        area = 0.5 * self.a * self.b * math.sin(rad_c)

        r_in = area / p
        r_out = c / (2 * math.sin(rad_c))

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ШАБЛОНОМ ---
        if "side" in self.targets:
            thm = self.db.get_theorem("Теорема косинусів")
            self._steps.append(f"➤ Знаходимо невідому сторону c:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: c = √(a² + b² - 2ab * cos(γ))")
            self._steps.append(
                f"Розв'язок: c = √({self.a}² + {self.b}² - 2*{self.a}*{self.b}*cos({self.angle_c}°)) = <span style='color: red; font-weight: bold;'>{c:.2f}</span>")
            result_data["side_c"] = round(c, 2)
        else:
            self._steps.append(f"ℹ️ Для подальших розрахунків невідома сторона c ≈ {c:.2f}")

        if "perimeter" in self.targets:
            self._steps.append(f"➤ Знаходимо периметр:")
            self._steps.append(f"Формула: P = a + b + c")
            self._steps.append(
                f"Розв'язок: P = {self.a} + {self.b} + {c:.2f} = <span style='color: red; font-weight: bold;'>{perim:.2f}</span>")
            result_data["perimeter"] = round(perim, 2)

        if "area" in self.targets:
            self._steps.append(f"➤ Знаходимо площу:")
            self._steps.append(f"Формула: S = 1/2 * a * b * sin(γ)")
            self._steps.append(
                f"Розв'язок: S = 0.5 * {self.a} * {self.b} * sin({self.angle_c}°) = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
            result_data["area"] = round(area, 2)

        if "incircle" in self.targets:
            thm = self.db.get_theorem("Радіус вписаного кола (трикутник)")
            self._steps.append(f"➤ Знаходимо радіус вписаного кола:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: r = S / p")
            self._steps.append(f"Проміжне значення: півпериметр p = {perim:.2f} / 2 = {p:.2f}")
            self._steps.append(
                f"Розв'язок: r = {area:.2f} / {p:.2f} = <span style='color: red; font-weight: bold;'>{r_in:.2f}</span>")
            result_data["r_inscribed"] = round(r_in, 2)

        if "circumcircle" in self.targets:
            self._steps.append(f"➤ Знаходимо радіус описаного кола:")
            self._steps.append(f"Правило: Оптимізовано через наслідок теореми синусів.")
            self._steps.append(f"Формула: R = c / (2 * sin(γ))")
            self._steps.append(
                f"Розв'язок: R = {c:.2f} / (2 * sin({self.angle_c}°)) = <span style='color: red; font-weight: bold;'>{r_out:.2f}</span>")
            result_data["r_circumscribed"] = round(r_out, 2)

        image_base64 = GeometryPlotter.plot_triangle(self.a, self.b, c)

        return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}


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

        # --- БАЗОВА МАТЕМАТИКА ---
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

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ШАБЛОНОМ ---
        if "side" in self.targets:
            thm_sin = self.db.get_theorem("Теорема синусів")
            self._steps.append(f"➤ Знаходимо третій кут та невідомі сторони:")

            self._steps.append(f"Формула (кут): α = 180° - β - γ")
            self._steps.append(
                f"Розв'язок (кут): α = 180° - {self.angle_b}° - {self.angle_c}° = <span style='color: red; font-weight: bold;'>{angle_a:.2f}°</span>")

            self._steps.append(f"Правило (сторони): {thm_sin['description']}")
            self._steps.append(f"Формула (сторона b): b = a * sin(β) / sin(α)")
            self._steps.append(
                f"Розв'язок (сторона b): b = {self.a} * sin({self.angle_b}°) / sin({angle_a}°) = <span style='color: red; font-weight: bold;'>{b:.2f}</span>")

            self._steps.append(f"Формула (сторона c): c = a * sin(γ) / sin(α)")
            self._steps.append(
                f"Розв'язок (сторона c): c = {self.a} * sin({self.angle_c}°) / sin({angle_a}°) = <span style='color: red; font-weight: bold;'>{c:.2f}</span>")

            result_data.update({"angle_a": round(angle_a, 2), "side_b": round(b, 2), "side_c": round(c, 2)})
        else:
            self._steps.append(f"ℹ️ Для подальших розрахунків визначаємо: α={angle_a}°, b≈{b:.2f}, c≈{c:.2f}")

        if "perimeter" in self.targets:
            self._steps.append(f"➤ Знаходимо периметр:")
            self._steps.append(f"Формула: P = a + b + c")
            self._steps.append(
                f"Розв'язок: P = {self.a} + {b:.2f} + {c:.2f} = <span style='color: red; font-weight: bold;'>{perim:.2f}</span>")
            result_data["perimeter"] = round(perim, 2)

        if "area" in self.targets:
            self._steps.append(f"➤ Знаходимо площу:")
            self._steps.append(f"Формула: S = 1/2 * b * c * sin(α)")
            self._steps.append(
                f"Розв'язок: S = 0.5 * {b:.2f} * {c:.2f} * sin({angle_a}°) = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
            result_data["area"] = round(area, 2)

        if "incircle" in self.targets:
            thm_in = self.db.get_theorem("Радіус вписаного кола (трикутник)")
            self._steps.append(f"➤ Знаходимо радіус вписаного кола:")
            self._steps.append(f"Правило: {thm_in['description']}")
            self._steps.append(f"Формула: r = S / p")
            self._steps.append(f"Проміжне значення: півпериметр p = {perim:.2f} / 2 = {p:.2f}")
            self._steps.append(
                f"Розв'язок: r = {area:.2f} / {p:.2f} = <span style='color: red; font-weight: bold;'>{r_in:.2f}</span>")
            result_data["r_inscribed"] = round(r_in, 2)

        if "circumcircle" in self.targets:
            self._steps.append(f"➤ Знаходимо радіус описаного кола:")
            self._steps.append(f"Правило: Оптимізовано через наслідок теореми синусів.")
            self._steps.append(f"Формула: R = a / (2 * sin(α))")
            self._steps.append(
                f"Розв'язок: R = {self.a} / (2 * sin({angle_a}°)) = <span style='color: red; font-weight: bold;'>{r_out:.2f}</span>")
            result_data["r_circumscribed"] = round(r_out, 2)

        image_base64 = GeometryPlotter.plot_triangle(self.a, b, c)

        return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}