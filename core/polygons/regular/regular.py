import math
from core.base import GeometricSolver
from core.polygons.regular.regular_plotter import RegularPolygonPlotter


class RegularPolygonSolver(GeometricSolver):
    """Розв'язувач для будь-якого правильного n-кутника."""

    def __init__(self, n: int, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.n = int(n)
        self.task_type = task_type
        self.side = 0.0
        self.R = 0.0  # Радіус описаного
        self.r = 0.0  # Радіус вписаного (апофема)

        # Витягуємо значення з params залежно від того, що прийшло
        self.val = float(next(iter(params.values()))) if params else 0.0

    def validate(self) -> bool:
        if self.n < 3:
            self._steps.append("Помилка: Кількість сторін має бути не менше 3.")
            return False
        if self.val <= 0:
            self._steps.append("Помилка: Значення параметра має бути додатним.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Правильний {self.n}-кутник")

        # 1. Нормалізація: Знаходимо сторону, R та r
        angle_rad = math.pi / self.n

        if self.task_type == "REGULAR_SIDE":
            self.side = self.val
            self.R = self.side / (2 * math.sin(angle_rad))
            self.r = self.side / (2 * math.tan(angle_rad))
            self._steps.append(f"Дано сторону a = {self.side}")

        elif self.task_type == "REGULAR_R_CIRCUM":
            self.R = self.val
            self.side = 2 * self.R * math.sin(angle_rad)
            self.r = self.R * math.cos(angle_rad)
            self._steps.append(f"Дано радіус описаного кола R = {self.R}")

        elif self.task_type == "REGULAR_R_IN":
            self.r = self.val
            self.side = 2 * self.r * math.tan(angle_rad)
            self.R = self.r / math.cos(angle_rad)
            self._steps.append(f"Дано радіус вписаного кола r = {self.r}")

        # 2. Обчислення за цілями
        if "area" in self.targets:
            area = (self.n * self.side * self.r) / 2
            result["area"] = self._add_step("Знаходимо площу", "S = (n * a * r) / 2",
                                            f"S = ({self.n} * {self.side:.2f} * {self.r:.2f}) / 2", area)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = n * a",
                                                 f"P = {self.n} * {self.side:.2f}", self.n * self.side)

        if "angles" in self.targets:
            sum_angles = (self.n - 2) * 180
            one_angle = sum_angles / self.n
            self._add_step("Сума внутрішніх кутів", "Σ = (n - 2) * 180°", f"Σ = ({self.n} - 2) * 180°", sum_angles)
            result["interior_angle"] = self._add_step("Один внутрішній кут", "α = Σ / n",
                                                      f"α = {sum_angles} / {self.n}", one_angle)

        if "radii" in self.targets:
            result["R_circum"] = round(self.R, 2)
            result["r_in"] = round(self.r, 2)
            self._steps.append(f"➤ Радіуси: R ≈ {self.R:.2f}, r ≈ {self.r:.2f}")

        image_base64 = RegularPolygonPlotter(self.n, self.side, self.R, self.r).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}