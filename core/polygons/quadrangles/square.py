import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rectangle_plotter import RectanglePlotter


class SquareTask(ABC):
    task_type: str
    input_target: str | None = None

    @abstractmethod
    def validate(self, solver: "SquareSolver") -> bool:
        pass

    @abstractmethod
    def normalize(self, solver: "SquareSolver", result: dict) -> None:
        pass


class SideTask(SquareTask):
    task_type = "SQUARE_SIDE"
    input_target = "side_a"

    def validate(self, solver: "SquareSolver") -> bool:
        if solver.a <= 0:
            solver.add_error("Сторона має бути додатною.")
            return False
        return True

    def normalize(self, solver: "SquareSolver", result: dict) -> None:
        solver.add_info(f"Квадрат: a={solver.a}")


class AreaTask(SquareTask):
    task_type = "SQUARE_AREA"
    input_target = "area"

    def validate(self, solver: "SquareSolver") -> bool:
        if solver.S <= 0:
            solver.add_error("Площа має бути додатною.")
            return False
        return True

    def normalize(self, solver: "SquareSolver", result: dict) -> None:
        solver.add_info(f"Квадрат: S={solver.S}")
        solver.a = math.sqrt(solver.S)
        solver.add_side_result(result, rule="Сторона квадрата дорівнює квадратному кореню з його площі.")


class PerimeterTask(SquareTask):
    task_type = "SQUARE_PERIMETER"
    input_target = "perimeter"

    def validate(self, solver: "SquareSolver") -> bool:
        if solver.P <= 0:
            solver.add_error("Периметр має бути додатним.")
            return False
        return True

    def normalize(self, solver: "SquareSolver", result: dict) -> None:
        solver.add_info(f"Квадрат: P={solver.P}")
        solver.a = solver.P / 4
        solver.add_side_result(
            result,
            formula="a = P / 4",
            solution=f"a = {solver.P} / 4",
            rule="Оскільки всі сторони квадрата рівні, сторона дорівнює чверті периметра.",
        )


class DiagonalTask(SquareTask):
    task_type = "SQUARE_DIAGONAL"
    input_target = "diagonal"

    def validate(self, solver: "SquareSolver") -> bool:
        if solver.d <= 0:
            solver.add_error("Діагональ має бути додатною.")
            return False
        return True

    def normalize(self, solver: "SquareSolver", result: dict) -> None:
        solver.add_info(f"Квадрат: d={solver.d}")
        solver.show_diagonal = True
        solver.a = solver.d / math.sqrt(2)
        solver.add_side_result(
            result,
            formula="a = d / sqrt(2)",
            solution=f"a = {solver.d} / sqrt(2)",
            rule="Сторона квадрата виражається через діагональ за теоремою Піфагора.",
        )


class SquareTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "SquareSolver", result: dict) -> None:
        pass


class AreaTarget(SquareTarget):
    target_name = "area"

    def calculate(self, solver: "SquareSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            "S = a^2",
            f"S = {solver.a:.2f}^2",
            solver.a ** 2,
            rule="Площа квадрата дорівнює квадрату його сторони.",
        )
        solver.step_num += 1


class PerimeterTarget(SquareTarget):
    target_name = "perimeter"

    def calculate(self, solver: "SquareSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = 4 * a",
            f"P = 4 * {solver.a:.2f}",
            4 * solver.a,
            rule="Периметр квадрата дорівнює сумі чотирьох його сторін.",
        )
        solver.step_num += 1


class DiagonalTarget(SquareTarget):
    target_name = "diagonal"

    def calculate(self, solver: "SquareSolver", result: dict) -> None:
        solver.add_diagonal_result(result, is_intermediate=False)


class IncircleTarget(SquareTarget):
    target_name = "incircle"

    def calculate(self, solver: "SquareSolver", result: dict) -> None:
        result["incircle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола r",
            "r = a / 2",
            f"r = {solver.a:.2f} / 2",
            solver.a / 2,
            rule="Радіус вписаного в квадрат кола дорівнює половині його сторони.",
        )
        solver.step_num += 1


class CircumcircleTarget(SquareTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "SquareSolver", result: dict) -> None:
        solver.add_diagonal_result(result, is_intermediate=not solver.is_target("diagonal"))
        solver.show_circumcircle = True
        solver.show_diagonal = True
        result["circumcircle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола R",
            "R = d / 2",
            f"R = {solver.d:.2f} / 2",
            solver.d / 2,
            rule="Радіус описаного кола дорівнює половині діагоналі.",
        )
        solver.step_num += 1


class SquareSolver(GeometricSolver):
    """Розв'язувач задач з квадратом."""

    TASKS: ClassVar[dict[str, SquareTask]] = {
        task.task_type: task
        for task in (
            SideTask(),
            AreaTask(),
            PerimeterTask(),
            DiagonalTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, SquareTarget]] = {
        target.target_name: target
        for target in (
            AreaTarget(),
            PerimeterTarget(),
            DiagonalTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "area",
        "perimeter",
        "diagonal",
        "incircle",
        "circumcircle",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.S = float(params.get("S", 0))
        self.P = float(params.get("P", 0))
        self.d = float(params.get("d", 0))
        self.show_diagonal = False
        self.show_circumcircle = False
        self._side_step_added = False
        self._diagonal_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для квадрата: {self.task_type}")
            return False
        return self.task.validate(self)

    def add_side_result(
        self,
        result: dict,
        formula: str = "a = sqrt(S)",
        solution: str | None = None,
        rule: str | None = None,
    ) -> float:
        if self._side_step_added:
            return self.a

        is_intermediate = not self.is_target("side_a")
        pref = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_side_a" if is_intermediate else "side_a"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {pref}Знаходимо сторону a",
            formula,
            solution or f"a = sqrt({self.S})",
            self.a,
            rule=rule,
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._side_step_added = True
        return self.a

    def add_diagonal_result(self, result: dict, is_intermediate: bool) -> float:
        if self.task_type == "SQUARE_DIAGONAL":
            return self.d
        if self._diagonal_step_added:
            return self.d

        self.d = self.a * math.sqrt(2)
        pref = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_diagonal" if is_intermediate else "diagonal"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {pref}Знаходимо діагональ d",
            "d = a * sqrt(2)",
            f"d = {self.a:.2f} * sqrt(2)",
            self.d,
            rule=(
                "Діагональ квадрата знаходиться за теоремою Піфагора."
                if not is_intermediate
                else "Діагональ необхідна для знаходження радіуса описаного кола."
            ),
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._diagonal_step_added = True
        if not is_intermediate:
            self.show_diagonal = True
        return self.d

    def _prepare(self) -> None:
        self.task.normalize(self, self._result)

    def _generate_image(self) -> str:
        return RectanglePlotter(
            self.a,
            self.a,
            d=self.d if getattr(self, "show_diagonal", False) else None,
            R_circum=self.d / 2 if getattr(self, "show_circumcircle", False) else None,
        ).plot()
