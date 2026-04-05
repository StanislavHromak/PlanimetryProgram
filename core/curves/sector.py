import math
from core.base import GeometricSolver
from core.curves.plotters.sector_plotter import SectorPlotter


class SectorSolver(GeometricSolver):
    """Розв'язувач задач для кругового сектора та сегмента."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.r = float(params.get('radius', 0))
        self.angle = float(params.get('angle', 0))

    def validate(self) -> bool:
        if self.r <= 0:
            self._add_error("Радіус має бути додатним.")
            return False
        if self.angle <= 0 or self.angle >= 360:
            self._add_error("Центральний кут має бути в межах від 0° до 360°.")
            return False
        return True

    def _calculate(self):
        self.step_num = 1
        result = {}
        rad_angle = math.radians(self.angle)

        self._add_info(f"Сектор: радіус r = {self.r}, центральний кут α = {self.angle}°")

        arc_length = (math.pi * self.r * self.angle) / 180
        if self._is_target("arc_length"):
            result["arc_length"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо довжину дуги L",
                "L = (π · r · α) / 180°",
                f"L = (π · {self.r} · {self.angle}°) / 180°",
                arc_length
            )
            self.step_num += 1

        sector_area = (math.pi * (self.r ** 2) * self.angle) / 360
        needs_sector_area = self._is_target("sector_area") or self._is_target("segment_area")

        if needs_sector_area:
            is_int = not self._is_target("sector_area")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_sector_area" if is_int else "sector_area"

            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо площу сектора",
                "S_сектора = (π · r² · α) / 360°",
                f"S_сектора = (π · {self.r}² · {self.angle}°) / 360°",
                sector_area,
                is_intermediate=is_int
            )
            self.step_num += 1

        if self._is_target("perimeter_sector"):
            p_sect = arc_length + 2 * self.r
            result["perimeter_sector"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо периметр сектора",
                "P = L + 2·r",
                f"P = {arc_length:.2f} + 2 · {self.r}",
                p_sect
            )
            self.step_num += 1

        chord_length = 2 * self.r * math.sin(rad_angle / 2)
        if self._is_target("chord_length"):
            result["chord_length"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо довжину хорди c",
                "c = 2 · r · sin(α / 2)",
                f"c = 2 · {self.r} · sin({self.angle}° / 2)",
                chord_length
            )
            self.step_num += 1

        if self._is_target("segment_area"):
            seg_area = (self.r ** 2 / 2) * (rad_angle - math.sin(rad_angle))
            result["segment_area"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо площу сегмента",
                "S_сегмента = S_сектора - (1/2 · r² · sin(α))",
                f"S_сегмента = {sector_area:.2f} - 0.5 · {self.r}² · sin({self.angle}°)",
                seg_area,
                rule="Площа кругового сегмента дорівнює площі сектора мінус площа трикутника, утвореного радіусами і хордою."
            )
            self.step_num += 1

        if self._is_target("segment_height"):
            h = self.r * (1 - math.cos(rad_angle / 2))
            result["segment_height"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо висоту сегмента (стрілу дуги)",
                "h = r · (1 - cos(α / 2))",
                f"h = {self.r} · (1 - cos({self.angle / 2}°))",
                h
            )
            self.step_num += 1

        image_base64 = SectorPlotter(self.r, self.angle).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}