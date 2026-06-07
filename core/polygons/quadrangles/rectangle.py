import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rectangle_plotter import RectanglePlotter


class RectangleTask(ABC):
    task_type: str
    input_target: str | None = None

    @abstractmethod
    def validate(self, solver: "RectangleSolver") -> bool:
        pass

    @abstractmethod
    def normalize(self, solver: "RectangleSolver", result: dict) -> None:
        pass


class SidesTask(RectangleTask):
    task_type = "RECTANGLE_SIDES"

    def validate(self, solver: "RectangleSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0:
            solver.add_error("Сторони прямокутника мають бути додатними.")
            return False
        return True

    def normalize(self, solver: "RectangleSolver", result: dict) -> None:
        solver.add_info(f"Прямокутник: a={solver.a}, b={solver.b}")


class AreaAndSideTask(RectangleTask):
    task_type = "RECTANGLE_AREA_SIDE"
    input_target = "area"

    def validate(self, solver: "RectangleSolver") -> bool:
        if solver.a <= 0 or solver.S <= 0:
            solver.add_error("Сторона та площа мають бути додатними.")
            return False
        return True

    def normalize(self, solver: "RectangleSolver", result: dict) -> None:
        solver.add_info(f"Прямокутник: a={solver.a}, S={solver.S}")
        solver.b = solver.S / solver.a
        solver.add_side_b_result(
            result,
            "b = S / a",
            f"b = {solver.S} / {solver.a}",
            "Друга сторона прямокутника дорівнює площі, поділеній на відому сторону.",
        )


class PerimeterAndSideTask(RectangleTask):
    task_type = "RECTANGLE_PERIMETER_SIDE"
    input_target = "perimeter"

    def validate(self, solver: "RectangleSolver") -> bool:
        if solver.a <= 0 or solver.P <= 0:
            solver.add_error("Сторона та периметр мають бути додатними.")
            return False
        if solver.P <= 2 * solver.a:
            solver.add_error("Периметр має бути більшим за подвоєну відому сторону.")
            return False
        return True

    def normalize(self, solver: "RectangleSolver", result: dict) -> None:
        solver.add_info(f"Прямокутник: a={solver.a}, P={solver.P}")
        solver.b = (solver.P / 2) - solver.a
        solver.add_side_b_result(
            result,
            "b = P / 2 - a",
            f"b = {solver.P} / 2 - {solver.a}",
            "Півпериметр дорівнює сумі суміжних сторін.",
        )


class DiagonalAndSideTask(RectangleTask):
    task_type = "RECTANGLE_DIAGONAL_SIDE"
    input_target = "diagonal"

    def validate(self, solver: "RectangleSolver") -> bool:
        if solver.a <= 0 or solver.d <= 0:
            solver.add_error("Сторона та діагональ мають бути додатними.")
            return False
        if solver.d <= solver.a:
            solver.add_error("Діагональ має бути більшою за будь-яку сторону прямокутника.")
            return False
        return True

    def normalize(self, solver: "RectangleSolver", result: dict) -> None:
        solver.add_info(f"Прямокутник: a={solver.a}, d={solver.d}")
        solver.show_diagonal = True
        solver.diag_val = solver.d
        solver.b = math.sqrt(solver.d ** 2 - solver.a ** 2)
        solver.add_side_b_result(
            result,
            "b = sqrt(d^2 - a^2)",
            f"b = sqrt({solver.d}^2 - {solver.a}^2)",
            "За теоремою Піфагора для трикутника, утвореного діагоналлю та сторонами.",
        )


class RectangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "RectangleSolver", result: dict) -> None:
        pass


class AreaTarget(RectangleTarget):
    target_name = "area"

    def calculate(self, solver: "RectangleSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу прямокутника",
            "S = a * b",
            f"S = {solver.a:.2f} * {solver.b:.2f}",
            solver.a * solver.b,
            rule="Площа прямокутника дорівнює добутку його суміжних сторін.",
        )
        solver.step_num += 1


class PerimeterTarget(RectangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "RectangleSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = 2 * (a + b)",
            f"P = 2 * ({solver.a:.2f} + {solver.b:.2f})",
            2 * (solver.a + solver.b),
            rule="Периметр дорівнює подвоєній сумі суміжних сторін.",
        )
        solver.step_num += 1


class DiagonalTarget(RectangleTarget):
    target_name = "diagonal"

    def calculate(self, solver: "RectangleSolver", result: dict) -> None:
        solver.add_diagonal_result(result, is_intermediate=False)


class CircumcircleTarget(RectangleTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "RectangleSolver", result: dict) -> None:
        solver.add_diagonal_result(result, is_intermediate=not solver.is_target("diagonal"))
        solver.show_circumcircle = True
        solver.show_diagonal = True
        result["r_circumscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола R",
            "R = d / 2",
            f"R = {solver.diag_val:.2f} / 2",
            solver.diag_val / 2,
            rule=(
                "Центр описаного кола лежить на перетині діагоналей, "
                "а радіус дорівнює половині діагоналі."
            ),
        )
        solver.step_num += 1


class RectangleSolver(GeometricSolver):
    """Розв'язувач задач з прямокутником."""

    TASKS: ClassVar[dict[str, RectangleTask]] = {
        task.task_type: task
        for task in (
            SidesTask(),
            AreaAndSideTask(),
            PerimeterAndSideTask(),
            DiagonalAndSideTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, RectangleTarget]] = {
        target.target_name: target
        for target in (
            AreaTarget(),
            PerimeterTarget(),
            DiagonalTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("area", "perimeter", "diagonal", "circumcircle")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.b = float(params.get("b", 0))
        self.S = float(params.get("S", 0))
        self.P = float(params.get("P", 0))
        self.d = float(params.get("d", 0))
        self.diag_val = self.d if self.d > 0 else 0.0
        self.show_diagonal = False
        self.show_circumcircle = False
        self._side_b_step_added = False
        self._diagonal_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для прямокутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def add_side_b_result(self, result: dict, formula: str, solution: str, rule: str) -> float:
        if self._side_b_step_added:
            return self.b

        is_intermediate = not self.is_target("side_b")
        prefix = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_side_b" if is_intermediate else "side_b"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо сторону b",
            formula,
            solution,
            self.b,
            rule=rule,
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._side_b_step_added = True
        return self.b

    def add_diagonal_result(self, result: dict, is_intermediate: bool) -> float:
        if self.task_type == "RECTANGLE_DIAGONAL_SIDE":
            self.diag_val = self.d
            return self.diag_val
        if self._diagonal_step_added:
            return self.diag_val

        self.diag_val = math.sqrt(self.a ** 2 + self.b ** 2)
        prefix = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_diagonal" if is_intermediate else "diagonal"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо діагональ d",
            "d = sqrt(a^2 + b^2)",
            f"d = sqrt({self.a:.2f}^2 + {self.b:.2f}^2)",
            self.diag_val,
            rule=(
                "Діагональ прямокутника знаходиться за теоремою Піфагора."
                if not is_intermediate
                else "Діагональ потрібна для знаходження радіуса описаного кола."
            ),
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._diagonal_step_added = True
        if not is_intermediate:
            self.show_diagonal = True
        return self.diag_val

    def _prepare(self) -> None:
        self.task.normalize(self, self._result)

    def _generate_image(self) -> str:
        return RectanglePlotter(
            self.a,
            self.b,
            d=self.diag_val if getattr(self, "show_diagonal", False) else None,
            R_circum=self.diag_val / 2 if getattr(self, "show_circumcircle", False) else None,
        ).plot()
