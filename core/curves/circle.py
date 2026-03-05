import math
from core.base import GeometricSolver
from core.plotter import GeometryPlotter


class CircleSolver(GeometricSolver):
    """Розв'язувач задач для кола та круга за різними початковими даними."""

    def __init__(self, known_type: str, val: float, targets: list = None):
        super().__init__(targets)
        self.known_type = known_type
        self.val = float(val)
        self.r = 0.0  # Радіус знайдемо пізніше

    def validate(self) -> bool:
        if self.val <= 0:
            self._steps.append("Помилка: Вхідне значення має бути додатним числом.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result_data = {}

        # --- 1. ПРИВЕДЕННЯ ДО БАЗИ (Шукаємо радіус) ---
        if self.known_type == "RADIUS":
            self.r = self.val
            self._steps.append(f"Дано: Коло з радіусом r = {self.r}")

        elif self.known_type == "DIAMETER":
            self.r = self.val / 2
            self._steps.append(f"Дано: Коло з діаметром d = {self.val}")
            self._steps.append(f"ℹ️ Проміжний крок: Знаходимо радіус r = d / 2 = {self.val} / 2 = {self.r:.2f}")

        elif self.known_type == "CIRCUMFERENCE":
            self.r = self.val / (2 * math.pi)
            self._steps.append(f"Дано: Коло з довжиною C = {self.val}")
            self._steps.append(
                f"ℹ️ Проміжний крок: Знаходимо радіус r = C / (2π) = {self.val} / (2*{math.pi:.4f}) ≈ {self.r:.2f}")

        elif self.known_type == "AREA":
            self.r = math.sqrt(self.val / math.pi)
            self._steps.append(f"Дано: Круг з площею S = {self.val}")
            self._steps.append(
                f"ℹ️ Проміжний крок: Знаходимо радіус r = √(S / π) = √({self.val} / {math.pi:.4f}) ≈ {self.r:.2f}")

        # --- 2. БАЗОВА МАТЕМАТИКА ---
        circumference = 2 * math.pi * self.r
        area = math.pi * (self.r ** 2)

        # --- 3. ФОРМУВАННЯ ЗВІТУ ЗА ШАБЛОНОМ ---
        if "perimeter" in self.targets or "circumference" in self.targets:
            thm_c = self.db.get_theorem("Довжина кола")
            self._steps.append(f"➤ Знаходимо довжину кола:")
            self._steps.append(f"Правило: {thm_c['description']}")
            self._steps.append(f"Формула: C = 2 * π * r")
            self._steps.append(
                f"Розв'язок: C = 2 * π * {self.r:.2f} = <span style='color: red; font-weight: bold;'>{circumference:.2f}</span>")
            result_data["circumference"] = round(circumference, 2)

        if "area" in self.targets:
            thm_s = self.db.get_theorem("Площа круга")
            self._steps.append(f"➤ Знаходимо площу круга:")
            self._steps.append(f"Правило: {thm_s['description']}")
            self._steps.append(f"Формула: S = π * r²")
            self._steps.append(
                f"Розв'язок: S = π * ({self.r:.2f})² = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
            result_data["area"] = round(area, 2)

        # Малюємо креслення
        image_base64 = GeometryPlotter.plot_circle(self.r)

        return {
            "success": True,
            "data": result_data,
            "steps": self._steps,
            "image": image_base64
        }


class CircleSectorSolver(GeometricSolver):
    """Розв'язувач задач для кругового сектора та хорди."""

    def __init__(self, radius: float, angle: float, targets: list = None):
        super().__init__(targets)
        self.r = float(radius)
        self.angle = float(angle)

    def validate(self) -> bool:
        if self.r <= 0:
            self._steps.append("Помилка: Радіус має бути додатним.")
            return False
        if self.angle <= 0 or self.angle >= 360:
            self._steps.append("Помилка: Центральний кут має бути в межах від 0 до 360 градусів.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        self._steps.append(f"Дано: Радіус r = {self.r}, Центральний кут α = {self.angle}°")
        result_data = {}

        # --- БАЗОВА МАТЕМАТИКА ---
        rad_angle = math.radians(self.angle)

        arc_length = (math.pi * self.r * self.angle) / 180
        sector_area = (math.pi * (self.r ** 2) * self.angle) / 360
        chord_length = 2 * self.r * math.sin(rad_angle / 2)

        # --- ФОРМУВАННЯ ЗВІТУ ЗА ШАБЛОНОМ ---
        if "arc" in self.targets:
            thm = self.db.get_theorem("Довжина дуги кола")
            self._steps.append(f"➤ Знаходимо довжину дуги:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: L = (π * r * α) / 180°")
            self._steps.append(
                f"Розв'язок: L = (π * {self.r} * {self.angle}°) / 180° = <span style='color: red; font-weight: bold;'>{arc_length:.2f}</span>")
            result_data["arc_length"] = round(arc_length, 2)

        if "sector_area" in self.targets:
            thm = self.db.get_theorem("Площа кругового сектора")
            self._steps.append(f"➤ Знаходимо площу сектора:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: S = (π * r² * α) / 360°")
            self._steps.append(
                f"Розв'язок: S = (π * {self.r}² * {self.angle}°) / 360° = <span style='color: red; font-weight: bold;'>{sector_area:.2f}</span>")
            result_data["sector_area"] = round(sector_area, 2)

        if "chord" in self.targets:
            thm = self.db.get_theorem("Довжина хорди")
            self._steps.append(f"➤ Знаходимо довжину хорди:")
            self._steps.append(f"Правило: {thm['description']}")
            self._steps.append(f"Формула: c = 2 * r * sin(α / 2)")
            self._steps.append(
                f"Розв'язок: c = 2 * {self.r} * sin({self.angle}° / 2) = <span style='color: red; font-weight: bold;'>{chord_length:.2f}</span>")
            result_data["chord_length"] = round(chord_length, 2)

        # Малюємо креслення
        image_base64 = GeometryPlotter.plot_circle_sector(self.r, self.angle)

        return {
            "success": True,
            "data": result_data,
            "steps": self._steps,
            "image": image_base64
        }