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
            r"L = \frac{\pi r \alpha}{180^\circ}",
            fr"L = \frac{{ \pi \cdot {solver.r} \cdot {solver.angle}^\circ }}{{ 180^\circ }}",
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
            r"P = L + 2r",
            fr"P = {solver.arc_length():.2f} + 2 \cdot {solver.r}",
            p_sect,
        )
        solver.step_num += 1


class ChordLengthTarget(SectorTarget):
    target_name = "chord_length"

    def calculate(self, solver: "SectorSolver", result: dict) -> None:
        result["chord_length"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо довжину хорди c",
            r"c = 2r \sin\left(\frac{\alpha}{2}\right)",
            fr"c = 2 \cdot {solver.r} \cdot \sin\left(\frac{{ {solver.angle}^\circ }}{{ 2 }}\right)",
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
            r"S_{\text{сегмента}} = S_{\text{сектора}} - \frac{1}{2} r^2 \sin(\alpha)",
            fr"S_{{\text{{сегмента}}}} = {sector_area:.2f} - \frac{{1}}{{2}} \cdot {solver.r}^2 \cdot \sin({solver.angle}^\circ)",
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
            r"h = r \left(1 - \cos\left(\frac{\alpha}{2}\right)\right)",
            fr"h = {solver.r} \left(1 - \cos\left(\frac{{ {solver.angle}^\circ }}{{ 2 }}\right)\right)",
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
            r"S_{\text{сектора}} = \frac{\pi r^2 \alpha}{360^\circ}",
            fr"S_{{\text{{сектора}}}} = \frac{{ \pi \cdot {self.r}^2 \cdot {self.angle}^\circ }}{{ 360^\circ }}",
            sector_area,
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._sector_area_step_added = True
        return sector_area

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)

    def _generate_image(self) -> str:
        draw_h = self.is_target("segment_height")

        return SectorPlotter(
            r=self.r,
            angle_deg=self.angle,
            draw_segment_height=draw_h
        ).plot()
