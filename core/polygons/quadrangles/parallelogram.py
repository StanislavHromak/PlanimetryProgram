import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.parallelogram_plotter import ParallelogramPlotter


class ParallelogramTask(ABC):
    task_type: str

    @staticmethod
    def validate_common_angle(solver: "ParallelogramSolver") -> bool:
        if solver.angle <= 0 or solver.angle >= 180:
            solver.add_error("Кут має бути в межах від 0 до 180 градусів.")
            return False
        return True

    @abstractmethod
    def validate(self, solver: "ParallelogramSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "ParallelogramSolver", result: dict) -> None:
        pass

    def add_prerequisites(self, solver: "ParallelogramSolver", result: dict) -> None:
        pass

    @abstractmethod
    def add_area_result(self, solver: "ParallelogramSolver", result: dict, is_intermediate: bool) -> float:
        pass

    @abstractmethod
    def add_angles_result(self, solver: "ParallelogramSolver", result: dict) -> None:
        pass

    @abstractmethod
    def add_height_result(self, solver: "ParallelogramSolver", result: dict) -> None:
        pass


class SidesAndAngleTask(ParallelogramTask):
    task_type = "PARALLELOGRAM_S_A"

    def validate(self, solver: "ParallelogramSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0:
            solver.add_error("Сторони мають бути додатними.")
            return False
        return self.validate_common_angle(solver)

    def prepare(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.add_info(f"Паралелограм: a={solver.a}, b={solver.b}, alpha={solver.angle}")
        solver.adj_angle_plot = solver.compute_adjacent_angle()
        solver.angle_plot = solver.angle
        solver.d1_plot = solver.compute_diagonal1_sa()
        solver.d2_plot = solver.compute_diagonal2_sa()

    def add_area_result(self, solver: "ParallelogramSolver", result: dict, is_intermediate: bool) -> float:
        area = solver.compute_area_sa()
        if solver.area_step_added:
            return area

        key = "intermediate_area" if is_intermediate else "area"
        pref = "(Проміжний крок) " if is_intermediate else ""
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо площу",
            "S = a * b * sin(alpha)",
            f"S = {solver.a} * {solver.b} * sin({solver.angle})",
            area,
            rule="Площа паралелограма дорівнює добутку двох сторін на синус кута між ними.",
            is_intermediate=is_intermediate,
        )
        solver.step_num += 1
        solver.area_step_added = True
        return area

    def add_angles_result(self, solver: "ParallelogramSolver", result: dict) -> None:
        result["adj_angle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сусідній кут",
            "beta = 180 - alpha",
            f"beta = 180 - {solver.angle}",
            solver.adj_angle_plot,
            rule="У паралелограмі суміжні кути в сумі дають 180 градусів.",
        )
        solver.step_num += 1

    def add_height_result(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.show_height = True
        solver.height_val = solver.compute_height_a()
        result["height_a"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту ha",
            "ha = b * sin(alpha)",
            f"ha = {solver.b} * sin({solver.angle})",
            solver.height_val,
            rule="Висота паралелограма до сторони a: ha = b * sin(alpha).",
        )
        solver.step_num += 1

        result["height_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту hb",
            "hb = a * sin(alpha)",
            f"hb = {solver.a} * sin({solver.angle})",
            solver.compute_height_b(),
            rule="Висота паралелограма до сторони b: hb = a * sin(alpha).",
        )
        solver.step_num += 1


class DiagonalsAndAngleTask(ParallelogramTask):
    task_type = "PARALLELOGRAM_D_A"

    def validate(self, solver: "ParallelogramSolver") -> bool:
        if solver.d1 <= 0 or solver.d2 <= 0:
            solver.add_error("Діагоналі мають бути додатними.")
            return False
        return self.validate_common_angle(solver)

    def prepare(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.add_info(
            f"Паралелограм: d1={solver.d1}, d2={solver.d2}, gamma={solver.angle} "
            "(кут між діагоналями)"
        )
        solver.d1_plot = solver.d1
        solver.d2_plot = solver.d2
        solver.a, solver.b = solver.compute_sides_from_diagonals()
        solver.angle_plot = solver.compute_angle_from_sides()
        solver.adj_angle_plot = 180.0 - solver.angle_plot

    def add_prerequisites(self, solver: "ParallelogramSolver", result: dict) -> None:
        if (
            solver.is_target("sides")
            or solver.is_target("perimeter")
            or solver.is_target("height")
            or solver.is_target("angles")
        ):
            solver.add_sides_from_diagonals_result(result, is_intermediate=not solver.is_target("sides"))

    def add_area_result(self, solver: "ParallelogramSolver", result: dict, is_intermediate: bool) -> float:
        area = solver.compute_area_da()
        if solver.area_step_added:
            return area

        key = "intermediate_area" if is_intermediate else "area"
        pref = "(Проміжний крок) " if is_intermediate else ""
        result[key] = solver.add_step(
            f"Крок {solver.step_num}. {pref}Знаходимо площу",
            "S = 1/2 * d1 * d2 * sin(gamma)",
            f"S = 1/2 * {solver.d1} * {solver.d2} * sin({solver.angle})",
            area,
            rule="Площа через діагоналі: половина їх добутку на синус кута між ними.",
            is_intermediate=is_intermediate,
        )
        solver.step_num += 1
        solver.area_step_added = True
        return area

    def add_angles_result(self, solver: "ParallelogramSolver", result: dict) -> None:
        result["angle_alpha"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут alpha між сторонами",
            "alpha = arccos((a^2 + b^2 - d1^2) / (2ab))",
            f"alpha = arccos(({solver.a:.2f}^2 + {solver.b:.2f}^2 - {solver.d1}^2) / (2*{solver.a:.2f}*{solver.b:.2f}))",
            solver.angle_plot,
            rule="Знаходимо за теоремою косинусів.",
        )
        solver.step_num += 1

        result["angle_beta"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо суміжний кут beta",
            "beta = 180 - alpha",
            f"beta = 180 - {solver.angle_plot:.1f}",
            solver.adj_angle_plot,
            rule="Сума суміжних кутів паралелограма дорівнює 180 градусів.",
        )
        solver.step_num += 1

    def add_height_result(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.show_height = True
        area = self.add_area_result(solver, result, is_intermediate=not solver.is_target("area"))
        solver.height_val = area / solver.a

        result["height_a"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту ha",
            "ha = S / a",
            f"ha = {area:.2f} / {solver.a:.2f}",
            solver.height_val,
            rule="Висота дорівнює відношенню площі до сторони, на яку вона проведена.",
        )
        solver.step_num += 1

        result["height_b"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту hb",
            "hb = S / b",
            f"hb = {area:.2f} / {solver.b:.2f}",
            area / solver.b,
            rule="Висота дорівнює відношенню площі до сторони, на яку вона проведена.",
        )
        solver.step_num += 1


class ParallelogramTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        pass


class SidesTarget(ParallelogramTarget):
    target_name = "sides"

    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        if solver.task_type == "PARALLELOGRAM_D_A":
            solver.add_sides_from_diagonals_result(result, is_intermediate=False)


class AreaTarget(ParallelogramTarget):
    target_name = "area"

    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.task.add_area_result(solver, result, is_intermediate=False)


class PerimeterTarget(ParallelogramTarget):
    target_name = "perimeter"

    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = 2 * (a + b)",
            f"P = 2 * ({solver.a:.2f} + {solver.b:.2f})",
            2 * (solver.a + solver.b),
            rule="Периметр паралелограма: P = 2*(a + b).",
        )
        solver.step_num += 1


class AnglesTarget(ParallelogramTarget):
    target_name = "angles"

    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.task.add_angles_result(solver, result)


class DiagonalsTarget(ParallelogramTarget):
    target_name = "diagonals"

    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        if solver.task_type != "PARALLELOGRAM_S_A":
            return

        result["diagonal_1"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо діагональ d1",
            "d1 = sqrt(a^2 + b^2 - 2*a*b*cos(alpha))",
            f"d1 = sqrt({solver.a}^2 + {solver.b}^2 - 2*{solver.a}*{solver.b}*cos({solver.angle}))",
            solver.d1_plot,
            rule="Теорема косинусів для трикутника, утвореного діагоналлю.",
        )
        solver.step_num += 1

        result["diagonal_2"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо діагональ d2",
            "d2 = sqrt(a^2 + b^2 + 2*a*b*cos(alpha))",
            f"d2 = sqrt({solver.a}^2 + {solver.b}^2 + 2*{solver.a}*{solver.b}*cos({solver.angle}))",
            solver.d2_plot,
        )
        solver.step_num += 1


class HeightTarget(ParallelogramTarget):
    target_name = "height"

    def calculate(self, solver: "ParallelogramSolver", result: dict) -> None:
        solver.task.add_height_result(solver, result)


class ParallelogramSolver(GeometricSolver):
    """Розв'язувач задач з паралелограмом."""

    TASKS: ClassVar[dict[str, ParallelogramTask]] = {
        task.task_type: task
        for task in (
            SidesAndAngleTask(),
            DiagonalsAndAngleTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, ParallelogramTarget]] = {
        target.target_name: target
        for target in (
            SidesTarget(),
            AreaTarget(),
            PerimeterTarget(),
            AnglesTarget(),
            DiagonalsTarget(),
            HeightTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "sides",
        "area",
        "perimeter",
        "angles",
        "diagonals",
        "height",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.b = float(params.get("b", 0))
        self.d1 = float(params.get("d1", 0))
        self.d2 = float(params.get("d2", 0))
        self.angle = float(params.get("angle", 0))
        self.d1_plot = self.d1
        self.d2_plot = self.d2
        self.angle_plot = self.angle
        self.adj_angle_plot = 0.0
        self.show_height = False
        self.height_val = 0.0
        self.sides_step_added = False
        self.area_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для паралелограма: {self.task_type}")
            return False
        return self.task.validate(self)

    def compute_adjacent_angle(self) -> float:
        return 180.0 - self.angle

    def compute_area_sa(self) -> float:
        if "area" in self._computed:
            return self._computed["area"]
        value = self.a * self.b * math.sin(math.radians(self.angle))
        self._computed["area"] = value
        return value

    def compute_height_a(self) -> float:
        if "h_a" in self._computed:
            return self._computed["h_a"]
        value = self.b * math.sin(math.radians(self.angle))
        self._computed["h_a"] = value
        return value

    def compute_height_b(self) -> float:
        if "h_b" in self._computed:
            return self._computed["h_b"]
        value = self.a * math.sin(math.radians(self.angle))
        self._computed["h_b"] = value
        return value

    def compute_diagonal1_sa(self) -> float:
        if "d1" in self._computed:
            return self._computed["d1"]
        rad = math.radians(self.angle)
        value = math.sqrt(max(0.0, self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad)))
        self._computed["d1"] = value
        return value

    def compute_diagonal2_sa(self) -> float:
        if "d2" in self._computed:
            return self._computed["d2"]
        rad = math.radians(self.angle)
        value = math.sqrt(max(0.0, self.a ** 2 + self.b ** 2 + 2 * self.a * self.b * math.cos(rad)))
        self._computed["d2"] = value
        return value

    def compute_sides_from_diagonals(self) -> tuple[float, float]:
        if "a" in self._computed and "b" in self._computed:
            return self._computed["a"], self._computed["b"]

        half1 = self.d1 / 2
        half2 = self.d2 / 2
        rad = math.radians(self.angle)

        a_val = math.sqrt(max(0.0, half1 ** 2 + half2 ** 2 - 2 * half1 * half2 * math.cos(rad)))
        b_val = math.sqrt(max(0.0, half1 ** 2 + half2 ** 2 + 2 * half1 * half2 * math.cos(rad)))

        self._computed["a"] = a_val
        self._computed["b"] = b_val
        return a_val, b_val

    def compute_angle_from_sides(self) -> float:
        if "angle_sides" in self._computed:
            return self._computed["angle_sides"]
        a, b = self.compute_sides_from_diagonals()
        cos_val = (a ** 2 + b ** 2 - self.d1 ** 2) / (2 * a * b)
        value = math.degrees(math.acos(max(-1.0, min(1.0, cos_val))))
        self._computed["angle_sides"] = value
        return value

    def compute_area_da(self) -> float:
        if "area" in self._computed:
            return self._computed["area"]
        value = 0.5 * self.d1 * self.d2 * math.sin(math.radians(self.angle))
        self._computed["area"] = value
        return value

    def add_sides_from_diagonals_result(self, result: dict, is_intermediate: bool) -> tuple[float, float]:
        if self.sides_step_added:
            return self.a, self.b

        prefix = "(Проміжний крок) " if is_intermediate else ""
        key_a = "intermediate_side_a" if is_intermediate else "side_a"
        key_b = "intermediate_side_b" if is_intermediate else "side_b"

        result[key_a] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо сторону a",
            "a = sqrt((d1/2)^2 + (d2/2)^2 - 2*(d1/2)*(d2/2)*cos(gamma))",
            f"a = sqrt({self.d1 / 2:.2f}^2 + {self.d2 / 2:.2f}^2 - 2*{self.d1 / 2:.2f}*{self.d2 / 2:.2f}*cos({self.angle}))",
            self.a,
            rule="Теорема косинусів для трикутника з половинами діагоналей.",
            is_intermediate=is_intermediate,
        )
        self.step_num += 1

        result[key_b] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо сторону b",
            "b = sqrt((d1/2)^2 + (d2/2)^2 + 2*(d1/2)*(d2/2)*cos(gamma))",
            f"b = sqrt({self.d1 / 2:.2f}^2 + {self.d2 / 2:.2f}^2 + 2*{self.d1 / 2:.2f}*{self.d2 / 2:.2f}*cos({self.angle}))",
            self.b,
            is_intermediate=is_intermediate,
        )
        self.step_num += 1
        self.sides_step_added = True
        return self.a, self.b

    def _calculate(self):
        self.step_num = 1
        result = {}

        self.task.prepare(self, result)
        self.task.add_prerequisites(self, result)

        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name):
                self.TARGETS[target_name].calculate(self, result)

        image_base64 = ParallelogramPlotter(
            self.a,
            self.b,
            self.angle_plot,
            opp_angle=self.adj_angle_plot,
            d1=self.d1_plot,
            d2=self.d2_plot,
            height=self.height_val if self.show_height else None,
        ).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}
