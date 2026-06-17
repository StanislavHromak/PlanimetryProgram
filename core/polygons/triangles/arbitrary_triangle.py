import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


COSINE_RULE = (
    "Теорема косинусів: квадрат сторони трикутника дорівнює сумі квадратів "
    "двох інших сторін мінус подвоєний добуток цих сторін на косинус кута між ними."
)
SINE_RULE = (
    "Теорема синусів: сторони трикутника пропорційні синусам протилежних кутів."
)


class ArbitraryTriangleTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "ArbitraryTriangleSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        pass

    @abstractmethod
    def ensure_sides(self, solver: "ArbitraryTriangleSolver") -> None:
        pass

    def add_side_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        self.ensure_sides(solver)

    def add_angle_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        pass


class SSSTask(ArbitraryTriangleTask):
    task_type = "SSS"

    def validate(self, solver: "ArbitraryTriangleSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0 or solver.c <= 0:
            solver.add_error("Сторони мають бути додатними.")
            return False
        if (
            solver.a + solver.b <= solver.c
            or solver.a + solver.c <= solver.b
            or solver.b + solver.c <= solver.a
        ):
            solver.add_error("Такий трикутник не існує, порушена нерівність трикутника.")
            return False
        return True

    def prepare(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.add_info(f"Довільний трикутник (SSS): a={solver.a}, b={solver.b}, c={solver.c}")

    def ensure_sides(self, solver: "ArbitraryTriangleSolver") -> None:
        pass

    # noinspection DuplicatedCode
    def add_angle_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        angle_a, angle_b, angle_c = solver.compute_angles_from_sides()

        result["angle_a"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут α",
            r"\alpha = \arccos\left(\frac{b^2 + c^2 - a^2}{2bc}\right)",
            f"\\alpha = \\arccos\\left(\\frac{{{solver.b:.2f}^2 + {solver.c:.2f}^2 - {solver.a:.2f}^2}}{{2 \\cdot {solver.b:.2f} \\cdot {solver.c:.2f}}}\\right)",
            round(angle_a, 2),
            rule=COSINE_RULE,
        )
        solver.step_num += 1

        result["angle_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут β",
            r"\beta = \arccos\left(\frac{a^2 + c^2 - b^2}{2ac}\right)",
            f"\\beta = \\arccos\\left(\\frac{{{solver.a:.2f}^2 + {solver.c:.2f}^2 - {solver.b:.2f}^2}}{{2 \\cdot {solver.a:.2f} \\cdot {solver.c:.2f}}}\\right)",
            round(angle_b, 2),
            rule="Теорема косинусів застосовується аналогічно для кожного кута.",
        )
        solver.step_num += 1

        result["angle_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут γ",
            r"\gamma = 180^\circ - \alpha - \beta",
            f"\\gamma = 180^\\circ - {angle_a:.2f}^\\circ - {angle_b:.2f}^\\circ",
            round(angle_c, 2),
            rule="Сума внутрішніх кутів трикутника дорівнює 180°.",
        )
        solver.step_num += 1


class SASTask(ArbitraryTriangleTask):
    task_type = "SAS"

    def validate(self, solver: "ArbitraryTriangleSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0 or solver.angle_c <= 0 or solver.angle_c >= 180:
            solver.add_error("Некоректні сторони або кут.")
            return False
        return True

    def prepare(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.add_info(
            f"Довільний трикутник (SAS): a={solver.a}, b={solver.b}, γ={solver.angle_c}°"
        )

    def ensure_sides(self, solver: "ArbitraryTriangleSolver") -> None:
        solver.c = solver.compute_side_c_sas()

    def add_side_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        self.ensure_sides(solver)
        result["side_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону c",
            r"c = \sqrt{a^2 + b^2 - 2ab \cdot \cos(\gamma)}",
            f"c = \\sqrt{{{solver.a:.2f}^2 + {solver.b:.2f}^2 - 2 \\cdot {solver.a:.2f} \\cdot {solver.b:.2f} \\cdot \\cos({solver.angle_c:.2f}^\\circ)}}",
            round(solver.c, 2),
            rule=COSINE_RULE,
        )
        solver.step_num += 1

    # noinspection DuplicatedCode
    def add_angle_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        self.ensure_sides(solver)
        angle_a, angle_b, _ = solver.compute_angles_from_sides()

        result["angle_a"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут α",
            r"\alpha = \arccos\left(\frac{b^2 + c^2 - a^2}{2bc}\right)",
            f"\\alpha = \\arccos\\left(\\frac{{{solver.b:.2f}^2 + {solver.c:.2f}^2 - {solver.a:.2f}^2}}{{2 \\cdot {solver.b:.2f} \\cdot {solver.c:.2f}}}\\right)",
            round(angle_a, 2),
            rule=COSINE_RULE,
        )
        solver.step_num += 1

        result["angle_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут β",
            r"\beta = \arccos\left(\frac{a^2 + c^2 - b^2}{2ac}\right)",
            f"\\beta = \\arccos\\left(\\frac{{{solver.a:.2f}^2 + {solver.c:.2f}^2 - {solver.b:.2f}^2}}{{2 \\cdot {solver.a:.2f} \\cdot {solver.c:.2f}}}\\right)",
            round(angle_b, 2),
            rule="Теорема косинусів застосовується аналогічно для кожного кута.",
        )
        solver.step_num += 1


class ASATask(ArbitraryTriangleTask):
    task_type = "ASA"

    def validate(self, solver: "ArbitraryTriangleSolver") -> bool:
        if (
            solver.a <= 0
            or solver.angle_b <= 0
            or solver.angle_c <= 0
            or solver.angle_b + solver.angle_c >= 180
        ):
            solver.add_error("Некоректна сторона або сума кутів >= 180 градусів.")
            return False
        return True

    def prepare(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.add_info(
            f"Довільний трикутник (ASA): a={solver.a}, β={solver.angle_b}°, γ={solver.angle_c}°"
        )

    def ensure_sides(self, solver: "ArbitraryTriangleSolver") -> None:
        solver.b, solver.c = solver.compute_sides_asa()

    def add_side_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.angle_a = 180 - solver.angle_b - solver.angle_c
        rad_a = math.radians(solver.angle_a)
        rad_b = math.radians(solver.angle_b)
        rad_c = math.radians(solver.angle_c)

        solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут α",
            r"\alpha = 180^\circ - \beta - \gamma",
            f"\\alpha = 180^\\circ - {solver.angle_b:.2f}^\\circ - {solver.angle_c:.2f}^\\circ",
            round(solver.angle_a, 2),
            rule="Сума внутрішніх кутів трикутника дорівнює 180°.",
        )
        solver.step_num += 1

        solver.b = (solver.a * math.sin(rad_b)) / math.sin(rad_a)
        result["side_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону b",
            r"b = \frac{a \cdot \sin(\beta)}{\sin(\alpha)}",
            f"b = \\frac{{{solver.a:.2f} \\cdot \\sin({solver.angle_b:.2f}^\\circ)}}{{\\sin({solver.angle_a:.2f}^\\circ)}}",
            round(solver.b, 2),
            rule=SINE_RULE,
        )
        solver.step_num += 1

        solver.c = (solver.a * math.sin(rad_c)) / math.sin(rad_a)
        result["side_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону c",
            r"c = \frac{a \cdot \sin(\gamma)}{\sin(\alpha)}",
            f"c = \\frac{{{solver.a:.2f} \\cdot \\sin({solver.angle_c:.2f}^\\circ)}}{{\\sin({solver.angle_a:.2f}^\\circ)}}",
            round(solver.c, 2),
        )
        solver.step_num += 1


class ArbitraryTriangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        pass


class SideTarget(ArbitraryTriangleTarget):
    target_name = "side"

    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.task.add_side_results(solver, result)


class AnglesTarget(ArbitraryTriangleTarget):
    target_name = "angles"

    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.task.add_angle_results(solver, result)


class PerimeterTarget(ArbitraryTriangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.task.ensure_sides(solver)
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            r"P = a + b + c",
            f"P = {solver.a:.2f} + {solver.b:.2f} + {solver.c:.2f}",
            round(solver.a + solver.b + solver.c, 2),
            rule="Периметр трикутника - сума довжин усіх його сторін.",
        )
        solver.step_num += 1


class AreaTarget(ArbitraryTriangleTarget):
    target_name = "area"

    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.task.ensure_sides(solver)
        p = solver.compute_semi_perimeter()
        area = solver.compute_area()
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу (формула Герона)",
            r"S = \sqrt{p(p-a)(p-b)(p-c)}",
            f"S = \\sqrt{{{p:.2f}({p:.2f}-{solver.a:.2f})({p:.2f}-{solver.b:.2f})({p:.2f}-{solver.c:.2f})}}",
            round(area, 2),
            rule="Формула Герона: площа обчислюється через півпериметр та три сторони.",
        )
        solver.step_num += 1


class IncircleTarget(ArbitraryTriangleTarget):
    target_name = "incircle"

    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.task.ensure_sides(solver)
        area = solver.compute_area()
        p = solver.compute_semi_perimeter()
        result["r_inscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола",
            r"r = \frac{S}{p}",
            f"r = \\frac{{{area:.2f}}}{{{p:.2f}}}",
            round(area / p, 2),
            rule="Радіус вписаного кола трикутника дорівнює площі, поділеній на півпериметр.",
        )
        solver.step_num += 1


class CircumcircleTarget(ArbitraryTriangleTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.task.ensure_sides(solver)
        area = solver.compute_area()
        r_out = (solver.a * solver.b * solver.c) / (4 * area)
        result["r_circumscribed"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус описаного кола",
            r"R = \frac{a \cdot b \cdot c}{4 \cdot S}",
            f"R = \\frac{{{solver.a:.2f} \\cdot {solver.b:.2f} \\cdot {solver.c:.2f}}}{{4 \\cdot {area:.2f}}}",
            round(r_out, 2),
            rule="Радіус описаного кола виражається через добуток сторін і площу.",
        )
        solver.step_num += 1


class ArbitraryTriangleSolver(GeometricSolver):
    """Розв'язувач задач для довільного трикутника (SSS, SAS, ASA)."""

    TASKS: ClassVar[dict[str, ArbitraryTriangleTask]] = {
        task.task_type: task
        for task in (
            SSSTask(),
            SASTask(),
            ASATask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, ArbitraryTriangleTarget]] = {
        target.target_name: target
        for target in (
            SideTarget(),
            AnglesTarget(),
            PerimeterTarget(),
            AreaTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "side",
        "angles",
        "perimeter",
        "area",
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
        self.angle_b = float(params.get("angle_b", 0))
        self.angle_c = float(params.get("angle_c", 0))
        self.angle_a = 0.0

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для довільного трикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def set_computed(self, key: str, value: float) -> None:
        """Сеттер для збереження проміжних розрахунків."""
        self._computed[key] = value

    def compute_angles_from_sides(self) -> tuple[float, float, float]:
        cos_a = (self.b ** 2 + self.c ** 2 - self.a ** 2) / (2 * self.b * self.c)
        cos_b = (self.a ** 2 + self.c ** 2 - self.b ** 2) / (2 * self.a * self.c)
        angle_a = math.degrees(math.acos(max(-1.0, min(1.0, cos_a))))
        angle_b = math.degrees(math.acos(max(-1.0, min(1.0, cos_b))))
        angle_c = 180 - angle_a - angle_b
        return angle_a, angle_b, angle_c

    def compute_side_c_sas(self) -> float:
        if "c" in self._computed:
            return self._computed["c"]

        rad_c = math.radians(self.angle_c)
        value = math.sqrt(self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad_c))

        if not self.is_target("side") and not self.is_target("angles"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо сторону c",
                r"c = \sqrt{a^2 + b^2 - 2ab \cdot \cos(\gamma)}",
                f"c = \\sqrt{{{self.a:.2f}^2 + {self.b:.2f}^2 - 2 \\cdot {self.a:.2f} \\cdot {self.b:.2f} \\cdot \\cos({self.angle_c:.2f}^\\circ)}}",
                round(value, 2),
                rule=COSINE_RULE,
                is_intermediate=True,
            )
            self.step_num += 1

        self.set_computed("c", value)
        return value

    def compute_sides_asa(self) -> tuple[float, float]:
        if "b" in self._computed and "c" in self._computed:
            return self._computed["b"], self._computed["c"]

        self.angle_a = 180 - self.angle_b - self.angle_c
        rad_a = math.radians(self.angle_a)
        rad_b = math.radians(self.angle_b)
        rad_c = math.radians(self.angle_c)

        b_val = (self.a * math.sin(rad_b)) / math.sin(rad_a)
        c_val = (self.a * math.sin(rad_c)) / math.sin(rad_a)

        if not self.is_target("side"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо кут α",
                r"\alpha = 180^\circ - \beta - \gamma",
                f"\\alpha = 180^\\circ - {self.angle_b:.2f}^\\circ - {self.angle_c:.2f}^\\circ",
                round(self.angle_a, 2),
                rule="Сума внутрішніх кутів трикутника дорівнює 180°.",
                is_intermediate=True,
            )
            self.step_num += 1
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо сторону b",
                r"b = \frac{a \cdot \sin(\beta)}{\sin(\alpha)}",
                f"b = \\frac{{{self.a:.2f} \\cdot \\sin({self.angle_b:.2f}^\\circ)}}{{\\sin({self.angle_a:.2f}^\\circ)}}",
                round(b_val, 2),
                rule=SINE_RULE,
                is_intermediate=True,
            )
            self.step_num += 1
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо сторону c",
                r"c = \frac{a \cdot \sin(\gamma)}{\sin(\alpha)}",
                f"c = \\frac{{{self.a:.2f} \\cdot \\sin({self.angle_c:.2f}^\\circ)}}{{\\sin({self.angle_a:.2f}^\\circ)}}",
                round(c_val, 2),
                is_intermediate=True,
            )
            self.step_num += 1

        self.set_computed("b", b_val)
        self.set_computed("c", c_val)
        return b_val, c_val

    def compute_semi_perimeter(self) -> float:
        if "p" in self._computed:
            return self._computed["p"]

        value = (self.a + self.b + self.c) / 2

        if not self.is_target("perimeter"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо напівпериметр p",
                r"p = \frac{a + b + c}{2}",
                f"p = \\frac{{{self.a:.2f} + {self.b:.2f} + {self.c:.2f}}}{{2}}",
                round(value, 2),
                is_intermediate=True,
            )
            self.step_num += 1

        self.set_computed("p", value)
        return value

    def compute_area(self) -> float:
        if "area" in self._computed:
            return self._computed["area"]

        p = self.compute_semi_perimeter()
        value = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

        if not self.is_target("area"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо площу",
                r"S = \sqrt{p(p-a)(p-b)(p-c)}",
                f"S = \\sqrt{{{p:.2f}({p:.2f}-{self.a:.2f})({p:.2f}-{self.b:.2f})({p:.2f}-{self.c:.2f})}}",
                round(value, 2),
                rule="Формула Герона: площа трикутника через три сторони та напівпериметр.",
                is_intermediate=True,
            )
            self.step_num += 1

        self.set_computed("area", value)
        return value

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)

    def _generate_image(self) -> str:
        self.task.ensure_sides(self)
        draw_in = self.is_target("incircle")
        draw_circ = self.is_target("circumcircle")
        return TrianglePlotter(
            self.a, self.b, self.c,
            draw_incircle=draw_in,
            draw_circumcircle=draw_circ
        ).plot()