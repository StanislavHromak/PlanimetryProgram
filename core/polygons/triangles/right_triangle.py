import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


PYTHAGOREAN_RULE = (
    "Теорема Піфагора: у прямокутному трикутнику квадрат гіпотенузи "
    "дорівнює сумі квадратів катетів."
)


class RightTriangleTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "RightTriangleSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "RightTriangleSolver", result: dict) -> None:
        pass

    @abstractmethod
    def add_side_result(self, solver: "RightTriangleSolver", result: dict) -> None:
        pass

    @abstractmethod
    def hypotenuse(self, solver: "RightTriangleSolver") -> float:
        pass

    @abstractmethod
    def second_leg(self, solver: "RightTriangleSolver") -> float:
        pass

    @abstractmethod
    def should_explain_hypotenuse(self) -> bool:
        pass

    @abstractmethod
    def should_explain_second_leg(self) -> bool:
        pass


class LegsTask(RightTriangleTask):
    task_type = "RIGHT_LEGS"

    def validate(self, solver: "RightTriangleSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0:
            solver.add_error("Катети мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "RightTriangleSolver", result: dict) -> None:
        solver.add_info(f"Прямокутний трикутник: катети a={solver.a}, b={solver.b}")

    def add_side_result(self, solver: "RightTriangleSolver", result: dict) -> None:
        c = solver.compute_hypotenuse()
        result["side_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо гіпотенузу",
            "c = sqrt(a^2 + b^2)",
            f"c = sqrt({solver.a}^2 + {solver.b}^2)",
            c,
            rule=PYTHAGOREAN_RULE,
        )
        solver.step_num += 1

    def hypotenuse(self, solver: "RightTriangleSolver") -> float:
        return math.sqrt(solver.a ** 2 + solver.b ** 2)

    def second_leg(self, solver: "RightTriangleSolver") -> float:
        return solver.b

    def should_explain_hypotenuse(self) -> bool:
        return True

    def should_explain_second_leg(self) -> bool:
        return False


class LegAndHypotenuseTask(RightTriangleTask):
    task_type = "RIGHT_LEG_HYPOTENUSE"

    def validate(self, solver: "RightTriangleSolver") -> bool:
        if solver.a <= 0 or solver.c <= 0:
            solver.add_error("Сторони мають бути додатними.")
            return False
        if solver.a >= solver.c:
            solver.add_error("Катет не може бути більшим або рівним гіпотенузі.")
            return False
        return True

    def prepare(self, solver: "RightTriangleSolver", result: dict) -> None:
        solver.add_info(
            f"Прямокутний трикутник: катет a={solver.a}, гіпотенуза c={solver.c}"
        )

    def add_side_result(self, solver: "RightTriangleSolver", result: dict) -> None:
        b = solver.compute_second_leg()
        result["side_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо другий катет",
            "b = sqrt(c^2 - a^2)",
            f"b = sqrt({solver.c}^2 - {solver.a}^2)",
            b,
            rule=PYTHAGOREAN_RULE,
        )
        solver.step_num += 1

    def hypotenuse(self, solver: "RightTriangleSolver") -> float:
        return solver.c

    def second_leg(self, solver: "RightTriangleSolver") -> float:
        return math.sqrt(solver.c ** 2 - solver.a ** 2)

    def should_explain_hypotenuse(self) -> bool:
        return False

    def should_explain_second_leg(self) -> bool:
        return True


class RightTriangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "RightTriangleSolver", result: dict) -> None:
        pass


class SideTarget(RightTriangleTarget):
    target_name = "side"

    def calculate(self, solver: "RightTriangleSolver", result: dict) -> None:
        solver.task.add_side_result(solver, result)


class AreaTarget(RightTriangleTarget):
    target_name = "area"

    def calculate(self, solver: "RightTriangleSolver", result: dict) -> None:
        b = solver.compute_second_leg()
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            "S = (a * b) / 2",
            f"S = ({solver.a} * {b:.2f}) / 2",
            (solver.a * b) / 2,
            rule="Площа прямокутного трикутника дорівнює половині добутку катетів.",
        )
        solver.step_num += 1


class PerimeterTarget(RightTriangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "RightTriangleSolver", result: dict) -> None:
        b = solver.compute_second_leg()
        c = solver.compute_hypotenuse()
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = a + b + c",
            f"P = {solver.a} + {b:.2f} + {c:.2f}",
            solver.a + b + c,
            rule="Периметр трикутника - сума довжин усіх його сторін.",
        )
        solver.step_num += 1


class IncircleTarget(RightTriangleTarget):
    target_name = "incircle"

    def calculate(self, solver: "RightTriangleSolver", result: dict) -> None:
        b = solver.compute_second_leg()
        c = solver.compute_hypotenuse()
        result["r_inscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола",
            "r = (a + b - c) / 2",
            f"r = ({solver.a} + {b:.2f} - {c:.2f}) / 2",
            (solver.a + b - c) / 2,
            rule="У прямокутному трикутнику радіус вписаного кола: r = (a + b - c) / 2.",
        )
        solver.step_num += 1


class CircumcircleTarget(RightTriangleTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "RightTriangleSolver", result: dict) -> None:
        c = solver.compute_hypotenuse()
        result["r_circumscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола",
            "R = c / 2",
            f"R = {c:.2f} / 2",
            c / 2,
            rule=(
                "У прямокутному трикутнику описане коло будується на гіпотенузі "
                "як на діаметрі, тому R = c / 2."
            ),
        )
        solver.step_num += 1


class RightTriangleSolver(GeometricSolver):
    """Розв'язувач задач для прямокутного трикутника."""

    TASKS: ClassVar[dict[str, RightTriangleTask]] = {
        task.task_type: task
        for task in (
            LegsTask(),
            LegAndHypotenuseTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, RightTriangleTarget]] = {
        target.target_name: target
        for target in (
            SideTarget(),
            AreaTarget(),
            PerimeterTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "side",
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
        self.b = float(params.get("b", 0))
        self.c = float(params.get("c", 0))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для прямокутного трикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def compute_hypotenuse(self) -> float:
        return self._compute_hypotenuse()

    def compute_second_leg(self) -> float:
        return self._compute_second_leg()

    def _compute_hypotenuse(self) -> float:
        if "c" in self._computed:
            return self._computed["c"]

        value = self.task.hypotenuse(self)

        if self.task.should_explain_hypotenuse() and not self.is_target("side"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо гіпотенузу",
                "c = sqrt(a^2 + b^2)",
                f"c = sqrt({self.a}^2 + {self.b}^2)",
                value,
                rule=PYTHAGOREAN_RULE,
                is_intermediate=True,
            )
            self.step_num += 1

        self._computed["c"] = value
        return value

    def _compute_second_leg(self) -> float:
        if "b" in self._computed:
            return self._computed["b"]

        value = self.task.second_leg(self)

        if self.task.should_explain_second_leg() and not self.is_target("side"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо другий катет",
                "b = sqrt(c^2 - a^2)",
                f"b = sqrt({self.c}^2 - {self.a}^2)",
                value,
                rule=PYTHAGOREAN_RULE,
                is_intermediate=True,
            )
            self.step_num += 1

        self._computed["b"] = value
        return value

    def _calculate(self):
        self.step_num = 1
        result = {}

        self.task.prepare(self, result)

        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name):
                self.TARGETS[target_name].calculate(self, result)

        b = self._compute_second_leg()
        c = self._compute_hypotenuse()
        image_base64 = TrianglePlotter(self.a, b, c).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
