import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.regular.regular_plotter import RegularPolygonPlotter


class RegularPolygonTask(ABC):
    task_type: str
    input_target: str | None = None

    @abstractmethod
    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        pass

    def validate(self, solver: "RegularPolygonSolver") -> bool:
        if solver.n < 3:
            solver.add_error("Кількість сторін має бути не менше 3.")
            return False
        if solver.val <= 0:
            solver.add_error("Значення параметра має бути додатним.")
            return False
        return True

    @abstractmethod
    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        pass


class SideTask(RegularPolygonTask):
    task_type = "REGULAR_SIDE"
    input_target = "side"

    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        solver.val = float(params.get("a", 0))

    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        solver.side = solver.val
        solver.add_info(f"Дано сторону a = {solver.side}")


class CircumradiusTask(RegularPolygonTask):
    task_type = "REGULAR_R_CIRCUM"
    input_target = "circumcircle"

    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        solver.val = float(params.get("R", 0))

    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        solver.add_info(f"Дано радіус описаного кола R = {solver.val}")
        is_int, pref, key = solver.get_step_info("side")
        solver.side = 2 * solver.val * math.sin(solver.angle_rad())
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо сторону a",
            "a = 2 * R * sin(180/n)",
            f"a = 2 * {solver.val} * sin(180/{solver.n})",
            solver.side,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class InradiusTask(RegularPolygonTask):
    task_type = "REGULAR_R_IN"
    input_target = "incircle"

    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        solver.val = float(params.get("r", 0))

    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        solver.add_info(f"Дано радіус вписаного кола r = {solver.val}")
        is_int, pref, key = solver.get_step_info("side")
        solver.side = 2 * solver.val * math.tan(solver.angle_rad())
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо сторону a",
            "a = 2 * r * tg(180/n)",
            f"a = 2 * {solver.val} * tg(180/{solver.n})",
            solver.side,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class AreaTask(RegularPolygonTask):
    task_type = "REGULAR_AREA"
    input_target = "area"

    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        solver.val = float(params.get("S", 0))

    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        solver.add_info(f"Дано площу S = {solver.val}")
        is_int, pref, key = solver.get_step_info("side")
        solver.side = math.sqrt((4 * solver.val * math.tan(solver.angle_rad())) / solver.n)
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо сторону a",
            "a = sqrt((4 * S * tg(180/n)) / n)",
            f"a = sqrt((4 * {solver.val} * tg(180/{solver.n})) / {solver.n})",
            solver.side,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class PerimeterTask(RegularPolygonTask):
    task_type = "REGULAR_PERIMETER"
    input_target = "perimeter"

    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        solver.val = float(params.get("P", 0))

    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        solver.add_info(f"Дано периметр P = {solver.val}")
        is_int, pref, key = solver.get_step_info("side")
        solver.side = solver.val / solver.n
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо сторону a",
            "a = P / n",
            f"a = {solver.val} / {solver.n}",
            solver.side,
            is_intermediate=is_int,
        )
        solver.step_num += 1


class AngleAndSideTask(RegularPolygonTask):
    task_type = "REGULAR_ANGLE_SIDE"
    input_target = "side"

    def read_params(self, solver: "RegularPolygonSolver", params: dict) -> None:
        solver.alpha = float(params.get("alpha", 0))
        solver.val = float(params.get("a", 0))

    def validate(self, solver: "RegularPolygonSolver") -> bool:
        if solver.alpha <= 0 or solver.alpha >= 180:
            solver.add_error("Внутрішній кут має бути в межах від 0 до 180 градусів.")
            return False
        if solver.val <= 0:
            solver.add_error("Сторона має бути додатною.")
            return False

        n_calc = 360 / (180 - solver.alpha)
        if not math.isclose(n_calc, round(n_calc), rel_tol=1e-3) or round(n_calc) < 3:
            solver.add_error(
                f"З кутом {solver.alpha} неможливо утворити правильний багатокутник "
                f"(вийшло n={n_calc:.2f})."
            )
            return False

        solver.n = int(round(n_calc))
        return True

    def normalize(self, solver: "RegularPolygonSolver", result: dict) -> None:
        solver.add_info(
            f"Дано внутрішній кут alpha = {solver.alpha} та сторону a = {solver.val}"
        )
        result["n_sides"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кількість сторін n",
            "n = 360 / (180 - alpha)",
            f"n = 360 / (180 - {solver.alpha}) = {solver.n}",
            solver.n,
            rule=(
                "Сума суміжних зовнішніх кутів дорівнює 360 градусів, "
                "а зовнішній кут дорівнює 180 - alpha."
            ),
        )
        solver.step_num += 1
        solver.side = solver.val


class RegularPolygonTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        pass


class AreaTarget(RegularPolygonTarget):
    target_name = "area"

    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        area = (solver.n * solver.side ** 2) / (4 * math.tan(solver.angle_rad()))
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            "S = (n * a^2) / (4 * tg(180/n))",
            f"S = ({solver.n} * {solver.side:.2f}^2) / (4 * tg(180/{solver.n}))",
            area,
        )
        solver.step_num += 1


class PerimeterTarget(RegularPolygonTarget):
    target_name = "perimeter"

    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        perimeter = solver.n * solver.side
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = n * a",
            f"P = {solver.n} * {solver.side:.2f}",
            perimeter,
        )
        solver.step_num += 1


class AnglesTarget(RegularPolygonTarget):
    target_name = "angles"

    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        sum_angles = (solver.n - 2) * 180
        one_angle = sum_angles / solver.n

        solver.add_step(
            f"Крок {solver.step_num}. (Проміжний крок) Знаходимо суму внутрішніх кутів",
            "sum = (n - 2) * 180",
            f"sum = ({solver.n} - 2) * 180",
            sum_angles,
            is_intermediate=True,
        )
        solver.step_num += 1

        if solver.task_type != "REGULAR_ANGLE_SIDE":
            result["interior_angle"] = solver.add_step(
                f"Крок {solver.step_num}. Знаходимо внутрішній кут",
                "alpha = sum / n",
                f"alpha = {sum_angles} / {solver.n}",
                one_angle,
            )
            solver.step_num += 1


class DiagonalTarget(RegularPolygonTarget):
    target_name = "diagonal"

    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        if solver.n <= 3:
            solver.add_info("У правильного трикутника немає діагоналей.")
            return

        solver.diag_val = 2 * solver.plot_R() * math.sin(2 * math.pi / solver.n)
        result["diagonal"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо найменшу діагональ d",
            "d = 2 * R * sin(360 / n)",
            f"d = 2 * {solver.plot_R():.2f} * sin(360 / {solver.n})",
            solver.diag_val,
            rule=(
                "Найменша діагональ правильного багатокутника з'єднує вершину "
                "через одну."
            ),
        )
        solver.step_num += 1


class CircumcircleTarget(RegularPolygonTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        solver.R = solver.plot_R()
        result["circumcircle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола R",
            "R = a / (2 * sin(180/n))",
            f"R = {solver.side:.2f} / (2 * sin(180/{solver.n}))",
            solver.R,
        )
        solver.step_num += 1


class IncircleTarget(RegularPolygonTarget):
    target_name = "incircle"

    def calculate(self, solver: "RegularPolygonSolver", result: dict) -> None:
        if solver.task.input_target == self.target_name:
            return

        solver.r = solver.plot_r()
        result["incircle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола r",
            "r = a / (2 * tg(180/n))",
            f"r = {solver.side:.2f} / (2 * tg(180/{solver.n}))",
            solver.r,
        )
        solver.step_num += 1


class RegularPolygonSolver(GeometricSolver):
    """Розв'язувач для будь-якого правильного n-кутника."""

    TASKS: ClassVar[dict[str, RegularPolygonTask]] = {
        task.task_type: task
        for task in (
            SideTask(),
            CircumradiusTask(),
            InradiusTask(),
            AreaTask(),
            PerimeterTask(),
            AngleAndSideTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, RegularPolygonTarget]] = {
        target.target_name: target
        for target in (
            AreaTarget(),
            PerimeterTarget(),
            AnglesTarget(),
            DiagonalTarget(),
            CircumcircleTarget(),
            IncircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "area",
        "perimeter",
        "angles",
        "diagonal",
        "circumcircle",
        "incircle",
    )

    def __init__(self, n: int, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.n = int(n)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.side = 0.0
        self.R = 0.0
        self.r = 0.0
        self.val = 0.0
        self.alpha = 0.0
        self.diag_val = None

        if self.task is not None:
            self.task.read_params(self, params)
        else:
            self.val = float(next(iter(params.values()))) if params else 0.0

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для правильного багатокутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def get_step_info(self, target_name: str) -> tuple[bool, str, str]:
        is_int = not self.is_target(target_name)
        pref = "(Проміжний крок) " if is_int else ""
        key = f"intermediate_{target_name}" if is_int else target_name
        return is_int, pref, key

    def angle_rad(self) -> float:
        return math.pi / self.n

    def plot_R(self) -> float:
        return self.side / (2 * math.sin(self.angle_rad()))

    def plot_r(self) -> float:
        return self.side / (2 * math.tan(self.angle_rad()))

    def _calculate(self):
        self.step_num = 1
        result = {}

        self.add_info(f"Фігура: Правильний {self.n}-кутник")
        self.task.normalize(self, result)

        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name):
                self.TARGETS[target_name].calculate(self, result)

        draw_R = self.is_target("circumcircle") or self.task_type == "REGULAR_R_CIRCUM"
        draw_r = self.is_target("incircle") or self.task_type == "REGULAR_R_IN"

        image_base64 = RegularPolygonPlotter(
            self.n,
            self.side,
            self.plot_R(),
            self.plot_r(),
            draw_R,
            draw_r,
            d=self.diag_val,
        ).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
