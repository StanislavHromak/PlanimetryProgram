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

    def add_angle_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        angle_a, angle_b, angle_c = solver.compute_angles_from_sides()

        result["angle_a"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут alpha",
            "alpha = arccos((b^2 + c^2 - a^2) / (2*b*c))",
            f"alpha = arccos(({solver.b}^2 + {solver.c}^2 - {solver.a}^2) / (2*{solver.b}*{solver.c}))",
            angle_a,
            rule="Теорема косинусів: cos(alpha) = (b^2 + c^2 - a^2) / (2*b*c).",
        )
        solver.step_num += 1

        result["angle_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут beta",
            "beta = arccos((a^2 + c^2 - b^2) / (2*a*c))",
            f"beta = arccos(({solver.a}^2 + {solver.c}^2 - {solver.b}^2) / (2*{solver.a}*{solver.c}))",
            angle_b,
            rule="Теорема косинусів застосовується аналогічно для кожного кута.",
        )
        solver.step_num += 1

        result["angle_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут gamma",
            "gamma = 180 - alpha - beta",
            f"gamma = 180 - {angle_a:.2f} - {angle_b:.2f}",
            angle_c,
            rule="Сума внутрішніх кутів трикутника дорівнює 180 градусів.",
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
            f"Довільний трикутник (SAS): a={solver.a}, b={solver.b}, gamma={solver.angle_c}"
        )

    def ensure_sides(self, solver: "ArbitraryTriangleSolver") -> None:
        solver.c = solver.compute_side_c_sas()

    def add_side_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        self.ensure_sides(solver)
        result["side_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону c",
            "c = sqrt(a^2 + b^2 - 2*a*b*cos(gamma))",
            f"c = sqrt({solver.a}^2 + {solver.b}^2 - 2*{solver.a}*{solver.b}*cos({solver.angle_c}))",
            solver.c,
            rule=COSINE_RULE,
        )
        solver.step_num += 1

    def add_angle_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        self.ensure_sides(solver)
        angle_a, angle_b, _ = solver.compute_angles_from_sides()

        result["angle_a"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут alpha",
            "alpha = arccos((b^2 + c^2 - a^2) / (2*b*c))",
            f"alpha = arccos(({solver.b}^2 + {solver.c:.2f}^2 - {solver.a}^2) / (2*{solver.b}*{solver.c:.2f}))",
            angle_a,
            rule="Теорема косинусів: cos(alpha) = (b^2 + c^2 - a^2) / (2*b*c).",
        )
        solver.step_num += 1

        result["angle_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут beta",
            "beta = arccos((a^2 + c^2 - b^2) / (2*a*c))",
            f"beta = arccos(({solver.a}^2 + {solver.c:.2f}^2 - {solver.b}^2) / (2*{solver.a}*{solver.c:.2f}))",
            angle_b,
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
            f"Довільний трикутник (ASA): a={solver.a}, beta={solver.angle_b}, gamma={solver.angle_c}"
        )

    def ensure_sides(self, solver: "ArbitraryTriangleSolver") -> None:
        solver.b, solver.c = solver.compute_sides_asa()

    def add_side_results(self, solver: "ArbitraryTriangleSolver", result: dict) -> None:
        solver.angle_a = 180 - solver.angle_b - solver.angle_c
        rad_a = math.radians(solver.angle_a)
        rad_b = math.radians(solver.angle_b)
        rad_c = math.radians(solver.angle_c)

        solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут alpha",
            "alpha = 180 - beta - gamma",
            f"alpha = 180 - {solver.angle_b} - {solver.angle_c}",
            solver.angle_a,
            rule="Сума внутрішніх кутів трикутника дорівнює 180 градусів.",
        )
        solver.step_num += 1

        solver.b = (solver.a * math.sin(rad_b)) / math.sin(rad_a)
        result["side_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону b",
            "b = a * sin(beta) / sin(alpha)",
            f"b = {solver.a} * sin({solver.angle_b}) / sin({solver.angle_a})",
            solver.b,
            rule=SINE_RULE,
        )
        solver.step_num += 1

        solver.c = (solver.a * math.sin(rad_c)) / math.sin(rad_a)
        result["side_c"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сторону c",
            "c = a * sin(gamma) / sin(alpha)",
            f"c = {solver.a} * sin({solver.angle_c}) / sin({solver.angle_a})",
            solver.c,
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
            "P = a + b + c",
            f"P = {solver.a:.2f} + {solver.b:.2f} + {solver.c:.2f}",
            solver.a + solver.b + solver.c,
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
            "S = sqrt(p*(p-a)*(p-b)*(p-c))",
            f"S = sqrt({p:.2f}*({p:.2f}-{solver.a:.2f})*({p:.2f}-{solver.b:.2f})*({p:.2f}-{solver.c:.2f}))",
            area,
            rule="Формула Герона: S = sqrt(p*(p-a)*(p-b)*(p-c)), де p = (a+b+c)/2.",
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
            "r = S / p",
            f"r = {area:.2f} / {p:.2f}",
            area / p,
            rule="Радіус вписаного кола трикутника: r = S / p.",
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
            "R = (a*b*c) / (4*S)",
            f"R = ({solver.a:.2f}*{solver.b:.2f}*{solver.c:.2f}) / (4*{area:.2f})",
            r_out,
            rule="Радіус описаного кола трикутника: R = (a*b*c) / (4*S).",
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
                "c = sqrt(a^2 + b^2 - 2*a*b*cos(gamma))",
                f"c = sqrt({self.a}^2 + {self.b}^2 - 2*{self.a}*{self.b}*cos({self.angle_c}))",
                value,
                rule=COSINE_RULE,
                is_intermediate=True,
            )
            self.step_num += 1

        self._computed["c"] = value
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
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо кут alpha",
                "alpha = 180 - beta - gamma",
                f"alpha = 180 - {self.angle_b} - {self.angle_c}",
                self.angle_a,
                rule="Сума внутрішніх кутів трикутника дорівнює 180 градусів.",
                is_intermediate=True,
            )
            self.step_num += 1
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо сторону b",
                "b = a * sin(beta) / sin(alpha)",
                f"b = {self.a} * sin({self.angle_b}) / sin({self.angle_a})",
                b_val,
                rule=SINE_RULE,
                is_intermediate=True,
            )
            self.step_num += 1
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо сторону c",
                "c = a * sin(gamma) / sin(alpha)",
                f"c = {self.a} * sin({self.angle_c}) / sin({self.angle_a})",
                c_val,
                is_intermediate=True,
            )
            self.step_num += 1

        self._computed["b"] = b_val
        self._computed["c"] = c_val
        return b_val, c_val

    def compute_semi_perimeter(self) -> float:
        if "p" in self._computed:
            return self._computed["p"]

        value = (self.a + self.b + self.c) / 2

        if not self.is_target("perimeter"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо напівпериметр p",
                "p = (a + b + c) / 2",
                f"p = ({self.a:.2f} + {self.b:.2f} + {self.c:.2f}) / 2",
                value,
                is_intermediate=True,
            )
            self.step_num += 1

        self._computed["p"] = value
        return value

    def compute_area(self) -> float:
        if "area" in self._computed:
            return self._computed["area"]

        p = self.compute_semi_perimeter()
        value = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

        if not self.is_target("area"):
            self.add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо площу",
                "S = sqrt(p*(p-a)*(p-b)*(p-c))",
                f"S = sqrt({p:.2f}*({p:.2f}-{self.a:.2f})*({p:.2f}-{self.b:.2f})*({p:.2f}-{self.c:.2f}))",
                value,
                rule="Формула Герона: площа трикутника через три сторони та напівпериметр.",
                is_intermediate=True,
            )
            self.step_num += 1

        self._computed["area"] = value
        return value

    def _calculate(self):
        self.step_num = 1
        result = {}

        self.task.prepare(self, result)

        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name):
                self.TARGETS[target_name].calculate(self, result)

        self.task.ensure_sides(self)

        image_base64 = TrianglePlotter(self.a, self.b, self.c).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
