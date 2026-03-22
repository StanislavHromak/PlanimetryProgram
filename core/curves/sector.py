import math
from core.base import GeometricSolver
from core.curves.plotters.sector_plotter import SectorPlotter

class SectorSolver(GeometricSolver):
    """Розв'язувач задач для кругового сектора та сегмента."""

    def __init__(self, radius: float, angle: float, targets: list = None):
        super().__init__(targets)
        self.r = float(radius)
        self.angle = float(angle)

    def validate(self) -> bool:
        if self.r <= 0:
            self._steps.append("Помилка: Радіус має бути додатним.")
            return False
        if self.angle <= 0 or self.angle >= 360:
            self._steps.append("Помилка: Центральний кут має бути в межах (0; 360).")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        self._steps.append(f"Дано: Радіус r = {self.r}, Центральний кут α = {self.angle}°")
        result = {}
        rad_angle = math.radians(self.angle)

        # 1. Довжина дуги (L) - ID: arc_length
        arc_length = (math.pi * self.r * self.angle) / 180
        if "arc_length" in self.targets:
            result["arc_length"] = self._add_step(
                "Довжина дуги",
                "L = (π * r * α) / 180°",
                f"L = (π * {self.r} * {self.angle}°) / 180°",
                arc_length
            )

        # 2. Площа сектора - ID: sector_area
        sector_area = (math.pi * (self.r ** 2) * self.angle) / 360
        if "sector_area" in self.targets:
            result["sector_area"] = self._add_step(
                "Площа сектора",
                "S_sect = (π * r² * α) / 360°",
                f"S_sect = (π * {self.r}² * {self.angle}°) / 360°",
                sector_area
            )

        # 3. Периметр сектора (Дуга + 2 радіуси) - ID: perimeter_sector
        if "perimeter_sector" in self.targets:
            p_sect = arc_length + 2 * self.r
            result["perimeter_sector"] = self._add_step(
                "Периметр сектора",
                "P = L + 2r",
                f"P = {arc_length:.2f} + 2 * {self.r}",
                p_sect
            )

        # 4. Хорда - ID: chord_length
        chord_length = 2 * self.r * math.sin(rad_angle / 2)
        if "chord_length" in self.targets:
            result["chord_length"] = self._add_step(
                "Довжина хорди",
                "c = 2 * r * sin(α / 2)",
                f"c = 2 * {self.r} * sin({self.angle}° / 2)",
                chord_length
            )

        # 5. Площа сегмента - ID: segment_area
        if "segment_area" in self.targets:
            # S_seg = S_sect - S_triangle = 1/2 * r^2 * (rad(α) - sin(α))
            seg_area = (self.r**2 / 2) * (rad_angle - math.sin(rad_angle))
            result["segment_area"] = self._add_step(
                "Площа сегмента",
                "S_seg = S_sect - (1/2 * r² * sin(α))",
                f"S_seg = {sector_area:.2f} - 0.5 * {self.r}² * sin({self.angle}°)",
                seg_area
            )

        # 6. Висота сегмента (стріла дуги) - ID: segment_height
        if "segment_height" in self.targets:
            h = self.r * (1 - math.cos(rad_angle / 2))
            result["segment_height"] = self._add_step(
                "Висота сегмента (стріла)",
                "h = r * (1 - cos(α / 2))",
                f"h = {self.r} * (1 - cos({self.angle / 2}°))",
                h
            )

        return {
            "success": True,
            "data": result,
            "steps": self._steps,
            "image": SectorPlotter(self.r, self.angle).plot()
        }