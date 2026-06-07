import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.curves.plotters.ellipse_plotter import EllipsePlotter


class EllipseTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "EllipseSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "EllipseSolver", result: dict) -> None:
        pass


class AxesTask(EllipseTask):
    task_type = "ELLIPSE_AXES"

    def validate(self, solver: "EllipseSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0:
            solver.add_error("Піввісі мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "EllipseSolver", result: dict) -> None:
        solver.add_info(f"Еліпс: велика піввісь a={solver.a}, мала піввісь b={solver.b}")


class EllipseTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "EllipseSolver", result: dict) -> None:
        pass


class AreaTarget(EllipseTarget):
    target_name = "area"

    def calculate(self, solver: "EllipseSolver", result: dict) -> None:
        area = math.pi * solver.a * solver.b
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            "S = pi * a * b",
            f"S = pi * {solver.a} * {solver.b}",
            area,
        )
        solver.step_num += 1


class PerimeterTarget(EllipseTarget):
    target_name = "perimeter"

    def calculate(self, solver: "EllipseSolver", result: dict) -> None:
        h = solver.ramanujan_h()
        solver.add_step(
            f"Крок {solver.step_num}. (Проміжний крок) Знаходимо допоміжний параметр h",
            "h = (a - b)^2 / (a + b)^2",
            f"h = ({solver.a} - {solver.b})^2 / ({solver.a} + {solver.b})^2",
            h,
            is_intermediate=True,
        )
        solver.step_num += 1

        term = (3 * h) / (10 + math.sqrt(4 - 3 * h))
        perim = math.pi * (solver.a + solver.b) * (1 + term)

        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр еліпса",
            "P ~= pi(a + b) * (1 + 3h / (10 + sqrt(4 - 3h)))",
            f"P ~= pi({solver.a} + {solver.b}) * (1 + (3 * {h:.4f}) / (10 + sqrt(4 - 3 * {h:.4f})))",
            perim,
            rule=(
                "Точного значення периметра еліпса не існує у вигляді простої формули. "
                "Використовується високоточне наближення Рамануджана."
            ),
        )
        solver.step_num += 1


class EccentricityTarget(EllipseTarget):
    target_name = "eccentricity"

    def calculate(self, solver: "EllipseSolver", result: dict) -> None:
        major = max(solver.a, solver.b)
        minor = min(solver.a, solver.b)
        ecc = math.sqrt(1 - (minor ** 2 / major ** 2))
        result["eccentricity"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо ексцентриситет",
            "e = sqrt(1 - (b/a)^2)",
            f"e = sqrt(1 - ({minor}/{major})^2)",
            ecc,
            rule="Ексцентриситет показує ступінь сплюснутості еліпса і лежить у межах від 0 до 1.",
        )
        solver.step_num += 1


class EllipseSolver(GeometricSolver):
    """Розв'язувач задач для еліпса."""

    TASKS: ClassVar[dict[str, EllipseTask]] = {
        task.task_type: task
        for task in (
            AxesTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, EllipseTarget]] = {
        target.target_name: target
        for target in (
            AreaTarget(),
            PerimeterTarget(),
            EccentricityTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("area", "perimeter", "eccentricity")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.b = float(params.get("b", 0))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для еліпса: {self.task_type}")
            return False
        return self.task.validate(self)

    def ramanujan_h(self) -> float:
        h_numerator = (self.a - self.b) ** 2
        h_denominator = (self.a + self.b) ** 2
        return h_numerator / h_denominator

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)

    def _generate_image(self) -> str:
        return EllipsePlotter(self.a, self.b).plot()
