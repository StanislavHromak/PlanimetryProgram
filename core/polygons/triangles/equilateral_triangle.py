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


class EquilateralTriangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        pass


class AreaTarget(EquilateralTriangleTarget):
    target_name = "area"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            "S = (a^2 * sqrt(3)) / 4",
            f"S = ({solver.a}^2 * sqrt(3)) / 4",
            (solver.a ** 2 * math.sqrt(3)) / 4,
            rule="Площа рівностороннього трикутника зі стороною a: S = (a^2*sqrt(3)) / 4.",
        )
        solver.step_num += 1


class PerimeterTarget(EquilateralTriangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = 3 * a",
            f"P = 3 * {solver.a}",
            3 * solver.a,
            rule="Периметр рівностороннього трикутника утричі більший за його сторону.",
        )
        solver.step_num += 1


class IncircleTarget(EquilateralTriangleTarget):
    target_name = "incircle"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        result["r_inscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола",
            "r = (a * sqrt(3)) / 6",
            f"r = ({solver.a} * sqrt(3)) / 6",
            (solver.a * math.sqrt(3)) / 6,
            rule="Радіус вписаного кола рівностороннього трикутника: r = a*sqrt(3) / 6.",
        )
        solver.step_num += 1


class CircumcircleTarget(EquilateralTriangleTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "EquilateralTriangleSolver", result: dict) -> None:
        result["r_circumscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола",
            "R = (a * sqrt(3)) / 3",
            f"R = ({solver.a} * sqrt(3)) / 3",
            (solver.a * math.sqrt(3)) / 3,
            rule="Радіус описаного кола рівностороннього трикутника: R = a*sqrt(3) / 3.",
        )
        solver.step_num += 1


class EquilateralTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівностороннього трикутника."""

    TASKS: ClassVar[dict[str, EquilateralTriangleTask]] = {
        task.task_type: task
        for task in (
            SideTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, EquilateralTriangleTarget]] = {
        target.target_name: target
        for target in (
            AreaTarget(),
            PerimeterTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
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

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для рівностороннього трикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)

    def _generate_image(self) -> str:
        return TrianglePlotter(self.a, self.a, self.a).plot()