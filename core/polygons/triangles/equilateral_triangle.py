import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class EquilateralTriangleTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "EquilateralTriangleSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        pass


class SideTask(EquilateralTriangleTask):
    task_type = "EQUILATERAL_SIDE"

    def validate(self, solver: "EquilateralTriangleSolver") -> bool:
        if solver.a <= 0:
            solver.add_error("Сторона має бути додатною.")
            return False
        return True

    def prepare(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        solver.add_info(f"Рівносторонній трикутник зі стороною a={solver.a}")


class AreaTask(EquilateralTriangleTask):
    """Зворотна задача: відома площа, знаходимо сторону."""
    task_type = "EQUILATERAL_AREA"

    def validate(self, solver: "EquilateralTriangleSolver") -> bool:
        if solver.given_area <= 0:
            solver.add_error("Площа має бути додатною.")
            return False
        return True

    def prepare(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        solver.add_info(f"Рівносторонній трикутник з площею S={solver.given_area}")
        solver.a = math.sqrt((4 * solver.given_area) / math.sqrt(3))
        result["side"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону через площу",
            r"a = \sqrt{\frac{4 \cdot S}{\sqrt{3}}}",
            f"a = \\sqrt{{\\frac{{4 \\cdot {solver.given_area:.2f}}}{{\\sqrt{{3}}}}}}",
            round(solver.a, 2),
            rule="Зворотна формула площі рівностороннього трикутника."
        )
        solver.step_num += 1


class HeightTask(EquilateralTriangleTask):
    """Зворотна задача: відома висота, знаходимо сторону."""
    task_type = "EQUILATERAL_HEIGHT"

    def validate(self, solver: "EquilateralTriangleSolver") -> bool:
        if solver.given_height <= 0:
            solver.add_error("Висота має бути додатною.")
            return False
        return True

    def prepare(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        solver.add_info(f"Рівносторонній трикутник з висотою h={solver.given_height}")
        solver.a = (2 * solver.given_height) / math.sqrt(3)
        result["side"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону через висоту",
            r"a = \frac{2 \cdot h}{\sqrt{3}}",
            f"a = \\frac{{2 \\cdot {solver.given_height:.2f}}}{{\\sqrt{{3}}}}",
            round(solver.a, 2),
            rule="Сторона рівностороннього трикутника виражена через його висоту."
        )
        solver.step_num += 1


class EquilateralTriangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        pass


class HeightTarget(EquilateralTriangleTarget):
    target_name = "height"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        val = (solver.a * math.sqrt(3)) / 2
        result["height"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту (медіану, бісектрису)",
            r"h = \frac{a \cdot \sqrt{3}}{2}",
            f"h = \\frac{{{solver.a:.2f} \\cdot \\sqrt{{3}}}}{{2}}",
            round(val, 2),
            rule="У рівносторонньому трикутнику висота, медіана і бісектриса співпадають.",
        )
        solver.step_num += 1


class AreaTarget(EquilateralTriangleTarget):
    target_name = "area"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        if solver.task_type == "EQUILATERAL_AREA":
            return

        val = (solver.a ** 2 * math.sqrt(3)) / 4
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            r"S = \frac{a^2 \cdot \sqrt{3}}{4}",
            f"S = \\frac{{{solver.a:.2f}^2 \\cdot \\sqrt{{3}}}}{{4}}",
            round(val, 2),
            rule="Площа рівностороннього трикутника зі стороною a.",
        )
        solver.step_num += 1


class PerimeterTarget(EquilateralTriangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        val = 3 * solver.a
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            r"P = 3 \cdot a",
            f"P = 3 \\cdot {solver.a:.2f}",
            round(val, 2),
            rule="Периметр рівностороннього трикутника утричі більший за його сторону.",
        )
        solver.step_num += 1


class IncircleTarget(EquilateralTriangleTarget):
    target_name = "incircle"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        val = (solver.a * math.sqrt(3)) / 6
        result["r_inscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола",
            r"r = \frac{a \cdot \sqrt{3}}{6}",
            f"r = \\frac{{{solver.a:.2f} \\cdot \\sqrt{{3}}}}{{6}}",
            round(val, 2),
            rule="Радіус вписаного кола рівностороннього трикутника.",
        )
        solver.step_num += 1


class CircumcircleTarget(EquilateralTriangleTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        val = (solver.a * math.sqrt(3)) / 3
        result["r_circumscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола",
            r"R = \frac{a \cdot \sqrt{3}}{3}",
            f"R = \\frac{{{solver.a:.2f} \\cdot \\sqrt{{3}}}}{{3}}",
            round(val, 2),
            rule="Радіус описаного кола рівностороннього трикутника.",
        )
        solver.step_num += 1


class EquilateralTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівностороннього трикутника."""

    TASKS: ClassVar[dict[str, EquilateralTriangleTask]] = {
        task.task_type: task
        for task in (
            SideTask(),
            AreaTask(),
            HeightTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, EquilateralTriangleTarget]] = {
        target.target_name: target
        for target in (
            HeightTarget(),
            AreaTarget(),
            PerimeterTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "height",
        "area",
        "perimeter",
        "incircle",
        "circumcircle",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.given_area = float(params.get("area", 0))
        self.given_height = float(params.get("height", 0))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для рівностороннього трикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)

    def _generate_image(self) -> str:
        draw_alt = self.is_target("height")
        draw_in = self.is_target("incircle")
        draw_circ = self.is_target("circumcircle")
        return TrianglePlotter(self.a, self.a, self.a, draw_altitude=draw_alt, draw_incircle=draw_in, draw_circumcircle=draw_circ).plot()