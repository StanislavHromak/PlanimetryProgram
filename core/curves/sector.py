import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.curves.plotters.sector_plotter import SectorPlotter


class SectorTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "SectorSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "SectorSolver", result: dict) -> None:
        pass


class RadiusAndAngleTask(SectorTask):
    task_type = "SECTOR_AND_ARC"

    def validate(self, solver: "SectorSolver") -> bool:
        if solver.r <= 0:
            solver.add_error("Радіус має бути додатним.")
            return False
        if solver.angle <= 0 or solver.angle >= 360:
            solver.add_error("Центральний кут має бути в межах від 0 до 360 градусів.")
            return False
        return True

    def prepare(self, solver: "SectorSolver", result: dict) -> None:
        solver.add_info(
            f"Сектор: радіус r = {solver.r}, центральний кут alpha = {solver.angle}"
        )


class SectorTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        pass


class ArcLengthTarget(SectorTarget):
    target_name = "arc_length"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        result["arc_length"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо довжину дуги L",
            "L = (pi * r * alpha) / 180",
            f"L = (pi * {solver.r} * {solver.angle}) / 180",
            solver.arc_length(),
        )
        solver.step_num += 1


class SectorAreaTarget(SectorTarget):
    target_name = "sector_area"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        solver.add_sector_area_result(result, is_intermediate=False)


class SectorPerimeterTarget(SectorTarget):
    target_name = "perimeter_sector"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        p_sect = solver.arc_length() + 2 * solver.r
        result["perimeter_sector"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр сектора",
            "P = L + 2*r",
            f"P = {solver.arc_length():.2f} + 2 * {solver.r}",
            p_sect,
        )
        solver.step_num += 1


class ChordLengthTarget(SectorTarget):
    target_name = "chord_length"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        result["chord_length"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо довжину хорди c",
            "c = 2 * r * sin(alpha / 2)",
            f"c = 2 * {solver.r} * sin({solver.angle} / 2)",
            solver.chord_length(),
        )
        solver.step_num += 1


class SegmentAreaTarget(SectorTarget):
    target_name = "segment_area"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        sector_area = solver.add_sector_area_result(
            result,
            is_intermediate=not solver.is_target("sector_area"),
        )
        seg_area = (solver.r ** 2 / 2) * (solver.rad_angle() - math.sin(solver.rad_angle()))
        result["segment_area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу сегмента",
            "S_segment = S_sector - (1/2 * r^2 * sin(alpha))",
            f"S_segment = {sector_area:.2f} - 0.5 * {solver.r}^2 * sin({solver.angle})",
            seg_area,
            rule=(
                "Площа кругового сегмента дорівнює площі сектора мінус площа "
                "трикутника, утвореного радіусами і хордою."
            ),
        )
        solver.step_num += 1


class SegmentHeightTarget(SectorTarget):
    target_name = "segment_height"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        h = solver.r * (1 - math.cos(solver.rad_angle() / 2))
        result["segment_height"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту сегмента",
            "h = r * (1 - cos(alpha / 2))",
            f"h = {solver.r} * (1 - cos({solver.angle / 2}))",
            h,
        )
        solver.step_num += 1


class SectorSolver(GeometricSolver):
    """Розв'язувач задач для кругового сектора та сегмента."""

    TASKS: ClassVar[dict[str, SectorTask]] = {
        task.task_type: task
        for task in (
            RadiusAndAngleTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, SectorTarget]] = {
        target.target_name: target
        for target in (
            ArcLengthTarget(),
            SectorAreaTarget(),
            SectorPerimeterTarget(),
            ChordLengthTarget(),
            SegmentAreaTarget(),
            SegmentHeightTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "arc_length",
        "sector_area",
        "perimeter_sector",
        "chord_length",
        "segment_area",
        "segment_height",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.r = float(params.get("radius", 0))
        self.angle = float(params.get("angle", 0))
        self._sector_area_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для сектора: {self.task_type}")
            return False
        return self.task.validate(self)

    def rad_angle(self) -> float:
        return math.radians(self.angle)

    def arc_length(self) -> float:
        return (math.pi * self.r * self.angle) / 180

    def sector_area(self) -> float:
        return (math.pi * (self.r ** 2) * self.angle) / 360

    def chord_length(self) -> float:
        return 2 * self.r * math.sin(self.rad_angle() / 2)

    def add_sector_area_result(self, result: dict, is_intermediate: bool) -> float:
        sector_area = self.sector_area()
        if self._sector_area_step_added:
            return sector_area

        pref = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_sector_area" if is_intermediate else "sector_area"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {pref}Знаходимо площу сектора",
            "S_sector = (pi * r^2 * alpha) / 360",
            f"S_sector = (pi * {self.r}^2 * {self.angle}) / 360",
            sector_area,
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._sector_area_step_added = True
        return sector_area

    def _calculate(self):
        self.step_num = 1
        result = {}

        self.task.prepare(self, result)

        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name):
                self.TARGETS[target_name].calculate(self, result)

        image_base64 = SectorPlotter(self.r, self.angle).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
