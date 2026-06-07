import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.curves.plotters.circle_plotter import CirclePlotter


class CircleTask(ABC):
    task_type: str
    input_target: str

    @staticmethod
    def validate(solver: "CircleSolver") -> bool:
        if solver.val <= 0:
            solver.add_error("Вхідне значення має бути додатним числом.")
            return False
        return True

    @abstractmethod
    def normalize(self, solver: "CircleSolver", result: dict) -> None:
        pass


class RadiusTask(CircleTask):
    task_type = "CIRCLE_RADIUS"
    input_target = "radius"

    def normalize(self, solver: "CircleSolver", result: dict) -> None:
        solver.r = solver.val
        solver.add_info(f"Дано: коло з радіусом r = {solver.r}")


class DiameterTask(CircleTask):
    task_type = "CIRCLE_DIAMETER"
    input_target = "diameter"

    def normalize(self, solver: "CircleSolver", result: dict) -> None:
        solver.add_info(f"Дано: коло з діаметром d = {solver.val}")
        is_int, pref, key = solver.get_step_info("radius")
        solver.r = solver.val / 2
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо радіус r",
            "r = d / 2",
            f"r = {solver.val} / 2",
            solver.r,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class CircumferenceTask(CircleTask):
    task_type = "CIRCLE_CIRCUMFERENCE"
    input_target = "circumference"

    def normalize(self, solver: "CircleSolver", result: dict) -> None:
        solver.add_info(f"Дано: коло з довжиною кола C = {solver.val}")
        is_int, pref, key = solver.get_step_info("radius")
        solver.r = solver.val / (2 * math.pi)
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо радіус r",
            "r = C / (2*pi)",
            f"r = {solver.val} / (2 * pi)",
            solver.r,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class AreaTask(CircleTask):
    task_type = "CIRCLE_AREA"
    input_target = "area"

    def normalize(self, solver: "CircleSolver", result: dict) -> None:
        solver.add_info(f"Дано: круг з площею S = {solver.val}")
        is_int, pref, key = solver.get_step_info("radius")
        solver.r = math.sqrt(solver.val / math.pi)
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо радіус r",
            "r = sqrt(S / pi)",
            f"r = sqrt({solver.val} / pi)",
            solver.r,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class CircleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "CircleSolver", result: dict) -> None:
        pass


class RadiusTarget(CircleTarget):
    target_name = "radius"

    def calculate(self, solver: "CircleSolver", result: dict) -> None:
        pass


class DiameterTarget(CircleTarget):
    target_name = "diameter"

    def calculate(self, solver: "CircleSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return
        result["diameter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо діаметр d",
            "d = 2 * r",
            f"d = 2 * {solver.r:.2f}",
            solver.r * 2,
        )
        solver.step_num += 1


class CircumferenceTarget(CircleTarget):
    target_name = "circumference"

    def calculate(self, solver: "CircleSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return
        result["circumference"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо довжину кола C",
            "C = 2 * pi * r",
            f"C = 2 * pi * {solver.r:.2f}",
            2 * math.pi * solver.r,
        )
        solver.step_num += 1


class CircleAreaTarget(CircleTarget):
    target_name = "area"

    def calculate(self, solver: "CircleSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу круга S",
            "S = pi * r^2",
            f"S = pi * ({solver.r:.2f})^2",
            math.pi * (solver.r ** 2),
        )
        solver.step_num += 1


class CircleSolver(GeometricSolver):
    """Розв'язувач задач для кола та круга за різними початковими даними."""

    TASKS: ClassVar[dict[str, CircleTask]] = {
        task.task_type: task
        for task in (
            RadiusTask(),
            DiameterTask(),
            CircumferenceTask(),
            AreaTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, CircleTarget]] = {
        target.target_name: target
        for target in (
            RadiusTarget(),
            DiameterTarget(),
            CircumferenceTarget(),
            CircleAreaTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "radius",
        "diameter",
        "circumference",
        "area",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.val = float(next(iter(params.values()))) if params else 0.0
        self.r = 0.0

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для кола: {self.task_type}")
            return False
        return self.task.validate(self)

    def get_step_info(self, target_name: str) -> tuple[bool, str, str]:
        is_int = not self.is_target(target_name)
        pref = "(Проміжний крок) " if is_int else ""
        key = f"intermediate_{target_name}" if is_int else target_name
        return is_int, pref, key

    def _prepare(self) -> None:
        self.task.normalize(self, self._result)

    def _generate_image(self) -> str:
        return CirclePlotter(self.r).plot()
