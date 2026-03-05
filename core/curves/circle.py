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