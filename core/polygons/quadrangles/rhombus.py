import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rhombus_plotter import RhombusPlotter


class RhombusTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "RhombusSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "RhombusSolver", result: dict) -> None:
        pass

    def add_prerequisites(self, solver: "RhombusSolver", result: dict) -> None:
        pass

    def add_angles_result(self, solver: "RhombusSolver", result: dict) -> None:
        solver.add_angles_from_diagonals_result(result)


class DiagonalsTask(RhombusTask):
    task_type = "RHOMBUS_DIAGONALS"

    def validate(self, solver: "RhombusSolver") -> bool:
        if solver.d1 <= 0 or solver.d2 <= 0:
            solver.add_error("Діагоналі мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "RhombusSolver", result: dict) -> None:
        solver.add_info(f"Ромб: d1={solver.d1}, d2={solver.d2}")
        solver.a = solver.compute_side_from_diagonals()
        solver.angle = solver.compute_angle_from_diagonals()

    def add_prerequisites(self, solver: "RhombusSolver", result: dict) -> None:
        if solver.is_target("side_a") or solver.is_target("perimeter") or solver.is_target("height"):
            solver.add_side_from_diagonals_result(result, is_intermediate=not solver.is_target("side_a"))


class SideAndAngleTask(RhombusTask):
    task_type = "RHOMBUS_SIDE_ANGLE"

    def validate(self, solver: "RhombusSolver") -> bool:
        if solver.a <= 0:
            solver.add_error("Сторона має бути додатною.")
            return False
        if solver.angle <= 0 or solver.angle >= 180:
            solver.add_error("Кут має бути в межах від 0° до 180°.")
            return False
        return True

    def prepare(self, solver: "RhombusSolver", result: dict) -> None:
        solver.add_info(f"Ромб: a={solver.a}, α={solver.angle}°")
        solver.d1, solver.d2 = solver.compute_diagonals_from_side_angle()

    def add_angles_result(self, solver: "RhombusSolver", result: dict) -> None:
        beta = 180.0 - solver.angle
        result["angle_beta"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо сусідній кут β",
            r"\beta = 180^\circ - \alpha",
            fr"\beta = 180^\circ - {solver.angle}^\circ",
            beta,
            rule="Сума суміжних кутів ромба дорівнює 180°."
        )
        solver.step_num += 1


class AreaAndSideTask(RhombusTask):
    task_type = "RHOMBUS_AREA_SIDE"

    def validate(self, solver: "RhombusSolver") -> bool:
        if solver.a <= 0 or solver.S <= 0:
            solver.add_error("Сторона і площа мають бути додатними.")
            return False
        if solver.S > solver.a ** 2:
            solver.add_error("Площа ромба не може перевищувати квадрат його сторони (S ≤ a²).")
            return False
        return True

    def prepare(self, solver: "RhombusSolver", result: dict) -> None:
        solver.add_info(f"Ромб: a={solver.a}, S={solver.S}")
        sin_alpha = solver.S / (solver.a ** 2)
        solver.angle = math.degrees(math.asin(sin_alpha))
        solver.d1, solver.d2 = solver.compute_diagonals_from_side_angle()

    def add_angles_result(self, solver: "RhombusSolver", result: dict) -> None:
        result["angle_alpha"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо гострий кут α",
            r"\alpha = \arcsin\left(\frac{S}{a^2}\right)",
            fr"\alpha = \arcsin\left(\frac{{ {solver.S} }}{{ {solver.a}^2 }}\right)",
            solver.angle,
            rule=r"З формули площі ромба через кут: \(S = a^2 \cdot \sin(\alpha)\)."
        )
        solver.step_num += 1

        beta = 180.0 - solver.angle
        result["angle_beta"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо тупий кут β",
            r"\beta = 180^\circ - \alpha",
            fr"\beta = 180^\circ - {solver.angle:.1f}^\circ",
            beta
        )
        solver.step_num += 1


class DiagonalAndSideTask(RhombusTask):
    task_type = "RHOMBUS_DIAGONAL_SIDE"

    def validate(self, solver: "RhombusSolver") -> bool:
        if solver.a <= 0 or solver.d1 <= 0:
            solver.add_error("Сторона і діагональ мають бути додатними.")
            return False
        if solver.d1 >= 2 * solver.a:
            solver.add_error("Діагональ ромба має бути строго меншою за подвоєну сторону.")
            return False
        return True

    def prepare(self, solver: "RhombusSolver", result: dict) -> None:
        solver.add_info(f"Ромб: a={solver.a}, відома діагональ d={solver.d1}")
        solver.d2 = solver.compute_other_diagonal_from_side()
        solver.angle = solver.compute_angle_from_diagonals()

    def add_prerequisites(self, solver: "RhombusSolver", result: dict) -> None:
        solver.add_other_diagonal_result(result, is_intermediate=not solver.is_target("diagonals"))


class RhombusTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        pass


class SideTarget(RhombusTarget):
    target_name = "side_a"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        if solver.task_type == "RHOMBUS_DIAGONALS":
            solver.add_side_from_diagonals_result(result, is_intermediate=False)


class AnglesTarget(RhombusTarget):
    target_name = "angles"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        solver.task.add_angles_result(solver, result)


class DiagonalsTarget(RhombusTarget):
    target_name = "diagonals"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        if solver.task_type == "RHOMBUS_SIDE_ANGLE":
            solver.add_diagonals_from_side_angle_result(result, is_intermediate=False)
        elif solver.task_type == "RHOMBUS_DIAGONAL_SIDE":
            solver.add_other_diagonal_result(result, is_intermediate=False)


class AreaTarget(RhombusTarget):
    target_name = "area"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        if solver.task_type == "RHOMBUS_AREA_SIDE":
            return
        if solver.task_type == "RHOMBUS_SIDE_ANGLE" and not solver.is_target("diagonals"):
            solver.add_diagonals_from_side_angle_result(result, is_intermediate=True)
        solver.add_area_result(result)


class PerimeterTarget(RhombusTarget):
    target_name = "perimeter"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            r"P = 4a",
            fr"P = 4 \cdot {solver.a:.2f}",
            4 * solver.a,
            rule="Усі сторони ромба рівні."
        )
        solver.step_num += 1


class HeightTarget(RhombusTarget):
    target_name = "height"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        height_val = solver.compute_height()
        result["height"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту h",
            r"h = \frac{S}{a}",
            fr"h = \frac{{ {solver.compute_area():.2f} }}{{ {solver.a:.2f} }}",
            height_val,
            rule="Висота дорівнює відношенню площі до сторони."
        )
        solver.step_num += 1


class IncircleTarget(RhombusTarget):
    target_name = "incircle"

    def calculate(self, solver: "RhombusSolver", result: dict) -> None:
        solver.show_incircle = True
        height_val = solver.compute_height()
        r_val = height_val / 2
        result["incircle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо радіус вписаного кола r",
            r"r = \frac{h}{2}",
            fr"r = \frac{{ {height_val:.2f} }}{{ 2 }}",
            r_val,
            rule="Центр вписаного кола лежить на перетині діагоналей, а радіус дорівнює половині висоти."
        )
        solver.step_num += 1


class RhombusSolver(GeometricSolver):
    """Розв'язувач задач з ромбом."""

    TASKS: ClassVar[dict[str, RhombusTask]] = {
        task.task_type: task
        for task in (
            DiagonalsTask(),
            SideAndAngleTask(),
            AreaAndSideTask(),
            DiagonalAndSideTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, RhombusTarget]] = {
        target.target_name: target
        for target in (
            SideTarget(),
            AnglesTarget(),
            DiagonalsTarget(),
            AreaTarget(),
            PerimeterTarget(),
            HeightTarget(),
            IncircleTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "side_a",
        "angles",
        "diagonals",
        "area",
        "perimeter",
        "height",
        "incircle",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.d1 = float(params.get("d1", 0))
        self.d2 = float(params.get("d2", 0))
        self.angle = float(params.get("angle", 0))
        self.S = float(params.get("S", 0))
        self.step_num = 1
        self.show_incircle = False
        self.side_step_added = False
        self.diagonals_step_added = False
        self.other_diagonal_step_added = False
        self.angles_step_added = False
        self.area_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для ромба: {self.task_type}")
            return False
        return self.task.validate(self)

    def compute_side_from_diagonals(self) -> float:
        if "side_a" in self._computed:
            return self._computed["side_a"]
        value = math.sqrt((self.d1 / 2) ** 2 + (self.d2 / 2) ** 2)
        self._computed["side_a"] = value
        return value

    def compute_angle_from_diagonals(self) -> float:
        if "angle" in self._computed:
            return self._computed["angle"]
        value = math.degrees(2 * math.atan(min(self.d1, self.d2) / max(self.d1, self.d2)))
        self._computed["angle"] = value
        return value

    def compute_diagonals_from_side_angle(self) -> tuple[float, float]:
        if "d1" in self._computed and "d2" in self._computed:
            return self._computed["d1"], self._computed["d2"]
        rad = math.radians(self.angle)
        d1_val = self.a * math.sqrt(max(0.0, 2 - 2 * math.cos(rad)))
        d2_val = self.a * math.sqrt(max(0.0, 2 + 2 * math.cos(rad)))
        self._computed["d1"] = d1_val
        self._computed["d2"] = d2_val
        return d1_val, d2_val

    def compute_other_diagonal_from_side(self) -> float:
        if "other_d2" in self._computed:
            return self._computed["other_d2"]
        value = 2 * math.sqrt(max(0.0, self.a ** 2 - (self.d1 / 2) ** 2))
        self._computed["other_d2"] = value
        return value

    def compute_area(self) -> float:
        if "area" in self._computed:
            return self._computed["area"]
        value = self.S if self.task_type == "RHOMBUS_AREA_SIDE" else 0.5 * self.d1 * self.d2
        self._computed["area"] = value
        return value

    def compute_height(self) -> float:
        if "height" in self._computed:
            return self._computed["height"]
        value = self.compute_area() / self.a
        self._computed["height"] = value
        return value

    def add_side_from_diagonals_result(self, result: dict, is_intermediate: bool) -> float:
        if self.side_step_added:
            return self.a

        prefix = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_side_a" if is_intermediate else "side_a"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо сторону a",
            r"a = \sqrt{\left(\frac{d_1}{2}\right)^2 + \left(\frac{d_2}{2}\right)^2}",
            fr"a = \sqrt{{ {self.d1 / 2:.2f}^2 + {self.d2 / 2:.2f}^2 }}",
            self.a,
            rule="Діагоналі ромба перетинаються під прямим кутом. Знаходимо за теоремою Піфагора.",
            is_intermediate=is_intermediate
        )
        self.step_num += 1
        self.side_step_added = True
        return self.a

    def add_diagonals_from_side_angle_result(self, result: dict, is_intermediate: bool) -> tuple[float, float]:
        if self.diagonals_step_added:
            return self.d1, self.d2

        prefix = "(Проміжний крок) " if is_intermediate else ""
        key1 = "intermediate_d1" if is_intermediate else "diagonal_1"
        key2 = "intermediate_d2" if is_intermediate else "diagonal_2"

        result[key1] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо діагональ d1",
            r"d_1 = a \sqrt{2 - 2\cos(\alpha)}",
            fr"d_1 = {self.a} \sqrt{{2 - 2\cos({self.angle}^\circ)}}",
            self.d1,
            rule="За теоремою косинусів.",
            is_intermediate=is_intermediate
        )
        self.step_num += 1
        result[key2] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо діагональ d2",
            r"d_2 = a \sqrt{2 + 2\cos(\alpha)}",
            fr"d_2 = {self.a} \sqrt{{2 + 2\cos({self.angle}^\circ)}}",
            self.d2,
            is_intermediate=is_intermediate
        )
        self.step_num += 1
        self.diagonals_step_added = True
        return self.d1, self.d2

    def add_other_diagonal_result(self, result: dict, is_intermediate: bool) -> float:
        if self.other_diagonal_step_added:
            return self.d2

        prefix = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_d2" if is_intermediate else "diagonal_2"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо іншу діагональ",
            r"d_2 = 2 \sqrt{a^2 - \left(\frac{d_1}{2}\right)^2}",
            fr"d_2 = 2 \sqrt{{ {self.a}^2 - \left(\frac{{ {self.d1} }}{{ 2 }}\right)^2 }}",
            self.d2,
            rule="З прямокутного трикутника, утвореного половинами діагоналей і стороною.",
            is_intermediate=is_intermediate
        )
        self.step_num += 1
        self.other_diagonal_step_added = True
        return self.d2

    def add_angles_from_diagonals_result(self, result: dict) -> None:
        if self.angles_step_added:
            return

        result["angle_alpha"] = self.add_step(
            f"Крок {self.step_num}. Знаходимо гострий кут α",
            r"\alpha = 2 \arctan\left(\frac{d_{min}}{d_{max}}\right)",
            fr"\alpha = 2 \arctan\left(\frac{{ {min(self.d1, self.d2)} }}{{ {max(self.d1, self.d2)} }}\right)",
            self.angle,
            rule="Половина діагоналей утворює зі стороною прямокутний трикутник."
        )
        self.step_num += 1

        beta = 180.0 - self.angle
        result["angle_beta"] = self.add_step(
            f"Крок {self.step_num}. Знаходимо тупий кут β",
            r"\beta = 180^\circ - \alpha",
            fr"\beta = 180^\circ - {self.angle:.1f}^\circ",
            beta,
            rule="Сума суміжних кутів ромба дорівнює 180°."
        )
        self.step_num += 1
        self.angles_step_added = True

    def add_area_result(self, result: dict) -> float:
        if self.area_step_added:
            return self.compute_area()

        area_val = self.compute_area()
        result["area"] = self.add_step(
            f"Крок {self.step_num}. Знаходимо площу",
            r"S = \frac{1}{2} d_1 d_2",
            fr"S = \frac{1}{2} \cdot {self.d1:.2f} \cdot {self.d2:.2f}",
            area_val,
            rule="Площа ромба дорівнює половині добутку його діагоналей."
        )
        self.step_num += 1
        self.area_step_added = True
        return area_val

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)
        self.task.add_prerequisites(self, self._result)

    def _generate_image(self) -> str:
        return RhombusPlotter(
            d1=self.d1,
            d2=self.d2,
            a=self.a,
            angle=self.angle,
            incircle_r=(self.compute_height() / 2) if getattr(self, "show_incircle", False) else None,
        ).plot()
