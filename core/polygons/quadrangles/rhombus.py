import math
from core.base import GeometricSolver
from plotters.rhombus_diagonals_plotter import RhombusDiagonalsPlotter
from plotters.parallelogram_plotter import ParallelogramPlotter


class RhombusSolver(GeometricSolver):
    """Розв'язувач задач для ромба (через діагоналі або сторону і кут)."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.d1 = float(params.get('d1', 0))
        self.d2 = float(params.get('d2', 0))
        self.a = float(params.get('a', 0))
        self.angle = float(params.get('angle', 0))

    def validate(self) -> bool:
        if self.task_type == "RHOMBUS_DIAGONALS":
            if self.d1 <= 0 or self.d2 <= 0:
                self._steps.append("Помилка: Діагоналі ромба мають бути додатними.")
                return False
        elif self.task_type == "RHOMBUS_SIDE_ANGLE":
            if self.a <= 0:
                self._steps.append("Помилка: Сторона ромба має бути додатною.")
                return False
            if self.angle <= 0 or self.angle >= 180:
                self._steps.append("Помилка: Кут має бути в межах від 0° до 180°.")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None

        if self.task_type == "RHOMBUS_DIAGONALS":
            self._steps.append(f"Фігура: Ромб з діагоналями d1={self.d1}, d2={self.d2}")
            side = math.sqrt((self.d1 / 2) ** 2 + (self.d2 / 2) ** 2)

            if "area" in self.targets:
                result["area"] = self._add_step("Знаходимо площу через діагоналі", "S = (d1 * d2) / 2",
                                                f"S = ({self.d1} * {self.d2}) / 2", (self.d1 * self.d2) / 2)

            if "perimeter" in self.targets:
                self._steps.append(
                    f"Проміжний крок: Знаходимо сторону через діагоналі a = √((d1/2)² + (d2/2)²) = {side:.2f}")
                result["perimeter"] = self._add_step("Знаходимо периметр", "P = 4 * a", f"P = 4 * {side:.2f}", 4 * side)

            if "incircle" in self.targets:
                result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = (d1 * d2) / (4 * a)",
                                                       f"r = ({self.d1} * {self.d2}) / (4 * {side:.2f})",
                                                       (self.d1 * self.d2) / (4 * side))

            image_base64 = RhombusDiagonalsPlotter(self.d1, self.d2).plot()

        elif self.task_type == "RHOMBUS_SIDE_ANGLE":
            self._steps.append(f"Фігура: Ромб зі стороною a={self.a} і кутом {self.angle}°")
            rad = math.radians(self.angle)
            area = self.a ** 2 * math.sin(rad)

            if "area" in self.targets:
                result["area"] = self._add_step("Знаходимо площу", "S = a² * sin(α)",
                                                f"S = {self.a}² * sin({self.angle}°)", area)
            if "perimeter" in self.targets:
                result["perimeter"] = self._add_step("Знаходимо периметр", "P = 4 * a", f"P = 4 * {self.a}", 4 * self.a)
            if "incircle" in self.targets:
                result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = S / (2 * a)",
                                                       f"r = {area:.2f} / (2 * {self.a})", area / (2 * self.a))

            image_base64 = ParallelogramPlotter(self.a, self.a, self.angle).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}