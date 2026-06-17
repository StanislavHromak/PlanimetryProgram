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


class BaseAndHeightTask(IsoscelesTriangleTask):
    task_type = "ISOSCELES_BASE_HEIGHT"

    def validate(self, solver: "IsoscelesTriangleSolver") -> bool:
        if solver.base <= 0 or solver.given_height <= 0:
            solver.add_error("Основа та висота мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        solver.add_info(f"Рівнобедрений трикутник: основа a={solver.base}, висота h={solver.given_height}")
        solver.side = math.sqrt(solver.given_height ** 2 + (solver.base / 2) ** 2)

        solver.set_computed("h", solver.given_height)
        solver._height_step_added = True

        result["side"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо бічну сторону за теоремою Піфагора",
            r"b = \sqrt{h^2 + \left(\frac{a}{2}\right)^2}",
            f"b = \\sqrt{{{solver.given_height:.2f}^2 + \\left(\\frac{{{solver.base:.2f}}}{{2}}\\right)^2}}",
            round(solver.side, 2),
            rule="Бічна сторона є гіпотенузою прямокутного трикутника, утвореного висотою та половиною основи."
        )
        solver.step_num += 1


class IsoscelesTriangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        pass


class SideTarget(IsoscelesTriangleTarget):
    target_name = "side"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        if solver.task_type == "ISOSCELES_BASE_HEIGHT":
            result["side"] = round(solver.side, 2)


class AngleBaseTarget(IsoscelesTriangleTarget):
    target_name = "angle_base"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        cos_alpha = (solver.base / 2) / solver.side
        alpha = math.degrees(math.acos(cos_alpha))
        result["angle_base"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут при основі (α)",
            r"\alpha = \arccos\left(\frac{a / 2}{b}\right)",
            f"\\alpha = \\arccos\\left(\\frac{{{solver.base:.2f} / 2}}{{{solver.side:.2f}}}\\right)",
            round(alpha, 2),
            rule="Кути при основі рівнобедреного трикутника рівні.",
        )
        solver.step_num += 1


class AngleVertexTarget(IsoscelesTriangleTarget):
    target_name = "angle_vertex"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        cos_alpha = (solver.base / 2) / solver.side
        alpha = math.degrees(math.acos(cos_alpha))
        beta = 180 - 2 * alpha
        result["angle_vertex"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут при вершині (β)",
            r"\beta = 180^\circ - 2\alpha",
            f"\\beta = 180^\\circ - 2 \\cdot {alpha:.1f}^\\circ",
            round(beta, 2),
            rule="Сума кутів трикутника дорівнює 180°."
        )
        solver.step_num += 1


class HeightTarget(IsoscelesTriangleTarget):
    target_name = "height"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        if solver.task_type == "ISOSCELES_BASE_HEIGHT":
            return
        solver.add_height_result(result, is_intermediate=False)


class AreaTarget(IsoscelesTriangleTarget):
    target_name = "area"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        h = solver.add_height_result(result, is_intermediate=not solver.is_target("height"))
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            r"S = \frac{a \cdot h}{2}",
            f"S = \\frac{{{solver.base:.2f} \\cdot {h:.2f}}}{{2}}",
            round((solver.base * h) / 2, 2),
            rule="Площа трикутника через основу і висоту.",
        )
        solver.step_num += 1


class PerimeterTarget(IsoscelesTriangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            r"P = a + 2 \cdot b",
            f"P = {solver.base:.2f} + 2 \\cdot {solver.side:.2f}",
            round(solver.base + 2 * solver.side, 2),
            rule="Периметр рівнобедреного трикутника: P = a + 2b.",
        )
        solver.step_num += 1


class IncircleTarget(IsoscelesTriangleTarget):
    target_name = "incircle"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        h = solver.compute_height()
        area = (solver.base * h) / 2
        p_half = (solver.base + 2 * solver.side) / 2
        result["r_inscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола",
            r"r = \frac{S}{p}",
            f"r = \\frac{{{area:.2f}}}{{{p_half:.2f}}}",
            round(area / p_half, 2),
            rule="Радіус вписаного кола дорівнює площі поділеній на півпериметр.",
        )
        solver.step_num += 1


class CircumcircleTarget(IsoscelesTriangleTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "IsoscelesTriangleSolver", result: dict) -> None:
        h = solver.compute_height()
        area = (solver.base * h) / 2
        result["r_circumscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола",
            r"R = \frac{a \cdot b^2}{4 \cdot S}",
            f"R = \\frac{{{solver.base:.2f} \\cdot {solver.side:.2f}^2}}{{4 \\cdot {area:.2f}}}",
            round((solver.base * solver.side ** 2) / (4 * area), 2),
            rule="Радіус описаного кола через сторони і площу.",
        )
        solver.step_num += 1


class IsoscelesTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівнобедреного трикутника."""

    TASKS: ClassVar[dict[str, IsoscelesTriangleTask]] = {
        task.task_type: task
        for task in (
            BaseAndSideTask(),
            BaseAndHeightTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, IsoscelesTriangleTarget]] = {
        target.target_name: target
        for target in (
            SideTarget(),
            AngleBaseTarget(),
            AngleVertexTarget(),
            HeightTarget(),
            AreaTarget(),
            PerimeterTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "side", "height", "angle_base", "angle_vertex", "area", "perimeter", "incircle", "circumcircle"
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.base = float(params.get("base", 0))
        self.side = float(params.get("side", 0))
        self.given_height = float(params.get("height", 0))
        self._height_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для рівнобедреного трикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def set_computed(self, key: str, value: float) -> None:
        """Сеттер для запису проміжних результатів, щоб уникнути доступу до _computed напряму."""
        self._computed[key] = value

    def compute_height(self) -> float:
        if "h" in self._computed:
            return self._computed["h"]

        value = math.sqrt(self.side ** 2 - (self.base / 2) ** 2)
        self.set_computed("h", value)
        return value

    def add_height_result(self, result: dict, is_intermediate: bool) -> float:
        h = self.compute_height()
        if self._height_step_added:
            return h

        pref = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_height" if is_intermediate else "height"

        result[key] = self.add_step(
            f"Крок {self.step_num}. {pref}Знаходимо висоту до основи",
            r"h = \sqrt{b^2 - \left(\frac{a}{2}\right)^2}",
            f"h = \\sqrt{{{self.side:.2f}^2 - \\left(\\frac{{{self.base:.2f}}}{{2}}\\right)^2}}",
            round(h, 2),
            rule=(
                "Висота рівнобедреного трикутника, опущена на основу, "
                "ділить її навпіл і є перпендикуляром."
            ),
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self._height_step_added = True
        return h

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)

    def _generate_image(self) -> str:
        draw_alt = self.is_target("height")
        draw_in = self.is_target("incircle")
        draw_circ = self.is_target("circumcircle")
        return TrianglePlotter(
            self.base, self.side, self.side,
            draw_altitude=draw_alt,
            draw_incircle=draw_in,
            draw_circumcircle=draw_circ
        ).plot()