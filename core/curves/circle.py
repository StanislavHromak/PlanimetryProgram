import math
from core.base import GeometricSolver
from .plotters.circle_plotter import CirclePlotter


class CircleSolver(GeometricSolver):
    """Розв'язувач задач для кола та круга за різними початковими даними."""

    def __init__(self, known_type: str, val: float, targets: list = None):
        super().__init__(targets)
        self.known_type = known_type
        self.val = float(val)
        self.r = 0.0

    def validate(self) -> bool:
        if self.val <= 0:
            self._steps.append("Помилка: Вхідне значення має бути додатним числом.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}

        # --- 1. ПРИВЕДЕННЯ ДО БАЗИ (Шукаємо радіус) ---
        if self.known_type == "RADIUS":
            self.r = self.val
            self._steps.append(f"Дано: Коло з радіусом r = {self.r}")

        elif self.known_type == "DIAMETER":
            self.r = self.val / 2
            self._steps.append(f"Дано: Коло з діаметром d = {self.val}")
            self._steps.append(f"ℹ️ Проміжний крок: Радіус — це половина діаметра: r = d / 2 = {self.val} / 2 = {self.r:.2f}")

        elif self.known_type == "CIRCUMFERENCE":
            self.r = self.val / (2 * math.pi)
            self._steps.append(f"Дано: Коло з довжиною C = {self.val}")
            self._steps.append(f"ℹ️ Проміжний крок: Знаходимо радіус r = C / (2π) = {self.val} / (2*{math.pi:.4f}) ≈ {self.r:.2f}")

        elif self.known_type == "AREA":
            self.r = math.sqrt(self.val / math.pi)
            self._steps.append(f"Дано: Круг з площею S = {self.val}")
            self._steps.append(f"ℹ️ Проміжний крок: Знаходимо радіус r = √(S / π) = √({self.val} / {math.pi:.4f}) ≈ {self.r:.2f}")

        # --- 2. ОБЧИСЛЕННЯ ЗАПИТАНИХ ПАРАМЕТРІВ ЗА ШАБЛОНОМ ---

        if "radius" in self.targets and self.known_type != "RADIUS":
            result["radius"] = self._add_step("Знаходимо радіус кола", "", "r", self.r)

        if "diameter" in self.targets and self.known_type != "DIAMETER":
            result["diameter"] = self._add_step("Знаходимо діаметр кола", "d = 2 * r", f"d = 2 * {self.r:.2f}", self.r * 2)

        if "perimeter" in self.targets or "circumference" in self.targets:
            if self.known_type != "CIRCUMFERENCE":
                result["circumference"] = self._add_step("Знаходимо довжину кола", "C = 2 * π * r", f"C = 2 * π * {self.r:.2f}", 2 * math.pi * self.r)

        if "area" in self.targets and self.known_type != "AREA":
            result["area"] = self._add_step("Знаходимо площу круга", "S = π * r²", f"S = π * ({self.r:.2f})²", math.pi * (self.r ** 2))

        image_base64 = CirclePlotter(self.r).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}