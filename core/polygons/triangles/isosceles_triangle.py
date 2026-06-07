import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class IsoscelesTriangleTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "IsoscelesTriangleSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        pass


class BaseAndSideTask(IsoscelesTriangleTask):
    task_type = "ISOSCELES_BASE_SIDE"

    def validate(self, solver: "IsoscelesTriangleSolver") -> bool:
        if solver.base <= 0 or solver.side <= 0:
            solver.add_error("Сторони мають бути додатними.")
            return False
        if solver.base >= 2 * solver.side:
            solver.add_error(
                "Основа має бути меншою за подвоєну бічну сторону "
                "(нерівність трикутника)."
            )
            return False
        return True

    def prepare(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        solver.add_info(
            f"Рівнобедрений трикутник: основа a={solver.base}, "
            f"бічна сторона b={solver.side}"
        )


class IsoscelesTriangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        pass


class HeightTarget(IsoscelesTriangleTarget):
    target_name = "height"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        solver.add_height_result(result, is_intermediate=False)


class AreaTarget(IsoscelesTriangleTarget):
    target_name = "area"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        h = solver.add_height_result(result, is_intermediate=not solver.is_target("height"))
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            "S = (a * h) / 2",
            f"S = ({solver.base} * {h:.2f}) / 2",
            (solver.base * h) / 2,
            rule="Площа трикутника через основу і висоту: S = (a * h) / 2.",
        )
        solver.step_num += 1


class PerimeterTarget(IsoscelesTriangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = a + 2*b",
            f"P = {solver.base} + 2*{solver.side}",
            solver.base + 2 * solver.side,
            rule="Периметр рівнобедреного трикутника: P = a + 2b.",
        )
        solver.step_num += 1


class IsoscelesTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівнобедреного трикутника."""

    TASKS: ClassVar[dict[str, IsoscelesTriangleTask]] = {
        task.task_type: task
        for task in (
            BaseAndSideTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, IsoscelesTriangleTarget]] = {
        target.target_name: target
        for target in (
            HeightTarget(),
            AreaTarget(),
            PerimeterTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("height", "area", "perimeter")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.base = float(params.get("base", 0))
        self.side = float(params.get("side", 0))
        self._height_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для рівнобедреного трикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def compute_height(self) -> float:
        if "h" in self._computed:
            return self._computed["h"]

        value = math.sqrt(self.side ** 2 - (self.base / 2) ** 2)
        self._computed["h"] = value
        return value

    def add_height_result(self, result: dict, is_intermediate: bool) -> float:
        h = self.compute_height()
        if self._height_step_added:
            return h

        pref = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_height" if is_intermediate else "height"

        result[key] = self.add_step(
            f"Крок {self.step_num}. {pref}Знаходимо висоту до основи",
            "h = sqrt(b^2 - (a/2)^2)",
            f"h = sqrt({self.side}^2 - ({self.base}/2)^2)",
            h,
            rule=(
                "Висота рівнобедреного трикутника, опущена на основу, "
                "ділить її навпіл і є перпендикуляром."
            ),
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._height_step_added = True
        return h

    def _calculate(self):
        self.step_num = 1
        result = {}

        self.task.prepare(self, result)

        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name):
                self.TARGETS[target_name].calculate(self, result)

        image_base64 = TrianglePlotter(self.base, self.side, self.side).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
