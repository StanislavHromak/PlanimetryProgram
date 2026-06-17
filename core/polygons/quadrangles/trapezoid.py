import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.trapezoid_plotter import TrapezoidPlotter


class TrapezoidTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "TrapezoidSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_prerequisites(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_midline_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_height_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_perimeter_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_angles_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_diagonals_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_incircle_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass

    def add_circumcircle_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass


class BasesAndHeightTask(TrapezoidTask):
    task_type = "TRAPEZOID_ABH"

    def validate(self, solver: "TrapezoidSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0 or solver.h <= 0:
            solver.add_error("Основи та висота мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_info(f"Трапеція: основи a={solver.a}, b={solver.b}, висота h={solver.h}")
        solver.plot_a = solver.a
        solver.plot_b = solver.b
        solver.plot_h = solver.h
        solver.plot_m = solver.compute_midline_from_bases()

    def add_prerequisites(self, solver: "TrapezoidSolver", result: dict) -> None:
        if solver.is_target("midline") or solver.is_target("area"):
            solver.add_midline_from_bases_result(result, is_intermediate=not solver.is_target("midline"))

    def add_midline_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_midline_from_bases_result(result, is_intermediate=False)


class AreaAndBasesTask(TrapezoidTask):
    task_type = "TRAPEZOID_AREA_BASES"

    def validate(self, solver: "TrapezoidSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0 or solver.S <= 0:
            solver.add_error("Основи та площа мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_info(f"Трапеція: основи a={solver.a}, b={solver.b}, площа S={solver.S}")
        solver.plot_a = solver.a
        solver.plot_b = solver.b
        solver.plot_m = solver.compute_midline_from_bases()
        solver.plot_h = solver.compute_height_from_area()

    def add_prerequisites(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_midline_from_bases_result(result, is_intermediate=not solver.is_target("midline"))

    def add_midline_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_midline_from_bases_result(result, is_intermediate=False)

    def add_height_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        result["height"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо висоту h",
            r"h = \frac{S}{m}",
            fr"h = \frac{{ {solver.S} }}{{ {solver.plot_m:.2f} }}",
            solver.plot_h,
            rule="З формули площі виражаємо висоту: відношення площі до середньої лінії."
        )
        solver.step_num += 1


class MidlineAndHeightTask(TrapezoidTask):
    task_type = "TRAPEZOID_MIDLINE_HEIGHT"

    def validate(self, solver: "TrapezoidSolver") -> bool:
        if solver.m <= 0 or solver.h <= 0:
            solver.add_error("Середня лінія та висота мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_info(f"Трапеція: середня лінія m={solver.m}, висота h={solver.h}")
        solver.plot_m = solver.m
        solver.plot_h = solver.h


class IsoscelesBasesAndLegTask(TrapezoidTask):
    task_type = "ISOSCELES_TRAPEZOID_BASES_LEG"

    def validate(self, solver: "TrapezoidSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0 or solver.c <= 0:
            solver.add_error("Основи та бічна сторона мають бути додатними.")
            return False
        diff = solver.compute_half_base_difference()
        if solver.c <= diff:
            solver.add_error("Бічна сторона занадто коротка. Вона має бути більшою за піврізницю основ.")
            return False
        return True

    def prepare(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.plot_type = "isosceles"
        solver.add_info(f"Рівнобічна трапеція: основи a={solver.a}, b={solver.b}, бічна сторона c={solver.c}")
        solver.plot_a = solver.a
        solver.plot_b = solver.b
        solver.plot_c = solver.c
        solver.plot_h = solver.compute_isosceles_height()
        solver.plot_m = solver.compute_midline_from_bases()

    def add_prerequisites(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_isosceles_projection_step()

        if (
            solver.is_target("height")
            or solver.is_target("area")
            or solver.is_target("diagonals")
            or solver.is_target("incircle")
            or solver.is_target("circumcircle")
        ):
            solver.add_isosceles_height_result(result, is_intermediate=not solver.is_target("height"))

        if (
            solver.is_target("midline")
            or solver.is_target("area")
            or solver.is_target("diagonals")
            or solver.is_target("circumcircle")
        ):
            solver.add_midline_from_bases_result(result, is_intermediate=not solver.is_target("midline"))

    def add_midline_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_midline_from_bases_result(result, is_intermediate=False)

    def add_height_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_isosceles_height_result(result, is_intermediate=False)

    def add_perimeter_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        p_val = solver.a + solver.b + 2 * solver.c
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = a + b + 2c",
            f"P = {solver.a} + {solver.b} + 2·{solver.c}",
            p_val
        )
        solver.step_num += 1

    def add_angles_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        diff = solver.compute_half_base_difference()
        alpha = math.degrees(math.acos(diff / solver.c))
        beta = 180.0 - alpha
        result["angle_alpha"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо гострий кут при основі α",
            "α = arccos(x / c)",
            f"α = arccos({diff:.2f} / {solver.c})",
            alpha
        )
        solver.step_num += 1
        result["angle_beta"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо тупий кут β",
            "β = 180° - α",
            f"β = 180° - {alpha:.1f}°",
            beta,
            rule="Сума кутів, прилеглих до бічної сторони, дорівнює 180°."
        )
        solver.step_num += 1

    def add_diagonals_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.d_val = solver.compute_isosceles_diagonal()
        result["diagonals"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо діагоналі (вони рівні)",
            "d = √(h² + m²)",
            f"d = √({solver.plot_h:.2f}² + {solver.plot_m:.2f}²)",
            solver.d_val,
            rule="Діагональ, висота та середня лінія рівнобічної трапеції утворюють прямокутний трикутник."
        )
        solver.step_num += 1

    def add_incircle_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_header(f"Крок {solver.step_num}. Перевірка вписаного кола")
        solver.step_num += 1
        if math.isclose(solver.a + solver.b, 2 * solver.c, rel_tol=1e-3):
            solver.add_info("Вписане коло існує (a + b = 2c).")
            result["incircle"] = solver.add_step(
                "Знаходимо радіус вписаного кола r",
                "r = h / 2",
                f"r = {solver.plot_h:.2f} / 2",
                solver.plot_h / 2,
                rule="Діаметр вписаного в трапецію кола дорівнює її висоті."
            )
        else:
            solver.add_info(f"Вписане коло не існує ({solver.a} + {solver.b} ≠ 2 · {solver.c}).")
            solver.add_rule("У трапецію можна вписати коло лише якщо сума основ дорівнює сумі бічних сторін.")

    def add_circumcircle_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_header(f"Крок {solver.step_num}. Описане коло")
        solver.step_num += 1
        solver.add_info("Описане коло існує (навколо рівнобічної трапеції завжди можна описати коло).")

        if solver.d_val is None:
            solver.d_val = solver.compute_isosceles_diagonal()
            solver.add_step(
                "(Проміжний крок) Знаходимо діагональ d",
                "d = √(h² + m²)",
                f"d = {solver.d_val:.2f}",
                solver.d_val,
                is_intermediate=True
            )

        r_circ = (solver.c * solver.d_val) / (2 * solver.plot_h)
        result["circumcircle"] = solver.add_step(
            "Знаходимо радіус описаного кола R",
            "R = (c · d) / (2 · h)",
            f"R = ({solver.c} · {solver.d_val:.2f}) / (2 · {solver.plot_h:.2f})",
            r_circ,
            rule="Радіус кола, описаного навколо рівнобічної трапеції, дорівнює радіусу кола навколо трикутника (основа, діагональ, бічна сторона)."
        )


class RightBasesAndHeightTask(TrapezoidTask):
    task_type = "RIGHT_TRAPEZOID_BASES_HEIGHT"

    def validate(self, solver: "TrapezoidSolver") -> bool:
        if solver.a <= 0 or solver.b <= 0 or solver.h <= 0:
            solver.add_error("Основи та висота мають бути додатними.")
            return False
        return True

    def prepare(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.plot_type = "right"
        solver.add_info(
            f"Прямокутна трапеція: основи a={solver.a}, b={solver.b}, "
            f"висота (бічна сторона) h={solver.h}"
        )
        solver.plot_a = solver.a
        solver.plot_b = solver.b
        solver.plot_h = solver.h
        solver.plot_m = solver.compute_midline_from_bases()

    def add_prerequisites(self, solver: "TrapezoidSolver", result: dict) -> None:
        if solver.is_target("midline") or solver.is_target("area"):
            solver.add_midline_from_bases_result(result, is_intermediate=not solver.is_target("midline"))
        if solver.is_target("perimeter") or solver.is_target("angles") or solver.is_target("incircle"):
            solver.add_right_slanted_side_step()

    def add_midline_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.add_midline_from_bases_result(result, is_intermediate=False)

    def add_perimeter_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        p_val = solver.a + solver.b + 2 * solver.c
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            r"P = a + b + 2c",
            fr"P = {solver.a} + {solver.b} + 2 \cdot {solver.c}",
            p_val
        )
        solver.step_num += 1

    def add_diagonals_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        d1 = math.sqrt(solver.a ** 2 + solver.h ** 2)
        result["diagonal_1"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо першу діагональ d1",
            r"d_1 = \sqrt{a^2 + h^2}",
            fr"d_1 = \sqrt{{ {solver.a}^2 + {solver.h}^2 }}",
            d1,
            rule="За теоремою Піфагора для прямокутного трикутника з катетами a (основа) та h (висота)."
        )
        solver.step_num += 1

        d2 = math.sqrt(solver.b ** 2 + solver.h ** 2)
        result["diagonal_2"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо другу діагональ d2",
            r"d_2 = \sqrt{b^2 + h^2}",
            fr"d_2 = \sqrt{{ {solver.b}^2 + {solver.h}^2 }}",
            d2,
            rule="За теоремою Піфагора для прямокутного трикутника з катетами b (друга основа) та h."
        )
        solver.step_num += 1

    def add_angles_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        diff = solver.compute_half_base_difference()
        alpha = math.degrees(math.acos(diff / solver.c))
        beta = 180.0 - alpha
        result["angle_alpha"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо гострий кут при основі α",
            r"\alpha = \arccos\left(\frac{x}{c}\right)",
            fr"\alpha = \arccos\left(\frac{{ {diff:.2f} }}{{ {solver.c} }}\right)",
            alpha
        )
        solver.step_num += 1
        result["angle_beta"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо тупий кут β",
            r"\beta = 180^\circ - \alpha",
            fr"\beta = 180^\circ - {alpha:.1f}^\circ",
            beta,
            rule="Сума кутів, прилеглих до бічної сторони, дорівнює 180°."
        )
        solver.step_num += 1

    def add_incircle_result(self, solver: "TrapezoidSolver", result: dict) -> None:
        c2_val = solver.compute_right_slanted_side()
        solver.add_header(f"Крок {solver.step_num}. Перевірка вписаного кола")
        solver.step_num += 1
        if math.isclose(solver.a + solver.b, solver.h + c2_val, rel_tol=1e-3):
            solver.add_info("Вписане коло існує (a + b = h + c_похила).")
            result["incircle"] = solver.add_step(
                "Знаходимо радіус вписаного кола r",
                r"r = \frac{h}{2}",
                fr"r = \frac{{ {solver.h:.2f} }}{{ 2 }}",
                solver.h / 2,
                rule="Діаметр вписаного в трапецію кола завжди дорівнює її висоті."
            )
        else:
            solver.add_info(f"Вписане коло не існує ({solver.a} + {solver.b} ≠ {solver.h} + {c2_val:.2f}).")
            solver.add_rule("У трапецію можна вписати коло лише якщо сума основ дорівнює сумі бічних сторін.")


class TrapezoidTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        pass


class MidlineTarget(TrapezoidTarget):
    target_name = "midline"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_midline_result(solver, result)


class HeightTarget(TrapezoidTarget):
    target_name = "height"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_height_result(solver, result)


class PerimeterTarget(TrapezoidTarget):
    target_name = "perimeter"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_perimeter_result(solver, result)


class AnglesTarget(TrapezoidTarget):
    target_name = "angles"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_angles_result(solver, result)


class DiagonalsTarget(TrapezoidTarget):
    target_name = "diagonals"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_diagonals_result(solver, result)


class IncircleTarget(TrapezoidTarget):
    target_name = "incircle"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_incircle_result(solver, result)


class CircumcircleTarget(TrapezoidTarget):
    target_name = "circumcircle"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        solver.task.add_circumcircle_result(solver, result)


class AreaTarget(TrapezoidTarget):
    target_name = "area"

    def calculate(self, solver: "TrapezoidSolver", result: dict) -> None:
        if solver.task_type == "TRAPEZOID_AREA_BASES":
            return

        area_val = solver.plot_m * solver.plot_h
        result["area"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо площу",
            r"S = m \cdot h",
            fr"S = {solver.plot_m:.2f} \cdot {solver.plot_h:.2f}",
            area_val,
            rule="Площа трапеції дорівнює добутку середньої лінії на висоту."
        )
        solver.step_num += 1


class TrapezoidSolver(GeometricSolver):
    """Розв'язувач задач з трапецією."""

    TASKS: ClassVar[dict[str, TrapezoidTask]] = {
        task.task_type: task
        for task in (
            BasesAndHeightTask(),
            AreaAndBasesTask(),
            MidlineAndHeightTask(),
            IsoscelesBasesAndLegTask(),
            RightBasesAndHeightTask(),
        )
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = (
        "TRAPEZOID_ABH",
        "TRAPEZOID_AREA_BASES",
        "TRAPEZOID_MIDLINE_HEIGHT",
        "ISOSCELES_TRAPEZOID_BASES_LEG",
    )

    TARGETS: ClassVar[dict[str, TrapezoidTarget]] = {
        target.target_name: target
        for target in (
            MidlineTarget(),
            HeightTarget(),
            PerimeterTarget(),
            AnglesTarget(),
            DiagonalsTarget(),
            IncircleTarget(),
            CircumcircleTarget(),
            AreaTarget(),
        )
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = (
        "midline",
        "height",
        "perimeter",
        "angles",
        "diagonals",
        "incircle",
        "circumcircle",
        "area",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get("a", 0))
        self.b = float(params.get("b", 0))
        self.h = float(params.get("h", 0))
        self.m = float(params.get("m", 0))
        self.S = float(params.get("S", 0))
        self.c = float(params.get("c", 0))
        self.step_num = 1
        self.plot_type = "arbitrary"
        self.plot_a = self.a
        self.plot_b = self.b
        self.plot_h = self.h
        self.plot_m = self.m
        self.plot_c = self.c
        self.d_val = None
        self.midline_step_added = False
        self.height_step_added = False
        self.projection_step_added = False
        self.right_slanted_side_step_added = False

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для трапеції: {self.task_type}")
            return False
        return self.task.validate(self)

    def compute_midline_from_bases(self) -> float:
        if "midline" in self._computed:
            return self._computed["midline"]
        value = (self.a + self.b) / 2
        self._computed["midline"] = value
        return value

    def compute_height_from_area(self) -> float:
        if "height_from_area" in self._computed:
            return self._computed["height_from_area"]
        value = self.S / self.compute_midline_from_bases()
        self._computed["height_from_area"] = value
        return value

    def compute_half_base_difference(self) -> float:
        return abs(self.a - self.b) / 2

    def compute_isosceles_height(self) -> float:
        if "isosceles_height" in self._computed:
            return self._computed["isosceles_height"]
        diff = self.compute_half_base_difference()
        value = math.sqrt(self.c ** 2 - diff ** 2)
        self._computed["isosceles_height"] = value
        return value

    def compute_isosceles_diagonal(self) -> float:
        if "isosceles_diagonal" in self._computed:
            return self._computed["isosceles_diagonal"]
        value = math.sqrt(self.plot_h ** 2 + self.plot_m ** 2)
        self._computed["isosceles_diagonal"] = value
        return value

    def compute_right_slanted_side(self) -> float:
        if "right_slanted_side" in self._computed:
            return self._computed["right_slanted_side"]
        diff = abs(self.a - self.b)
        value = math.sqrt(self.h ** 2 + diff ** 2)
        self._computed["right_slanted_side"] = value
        return value

    def add_midline_from_bases_result(self, result: dict, is_intermediate: bool) -> float:
        if self.midline_step_added:
            return self.plot_m

        prefix = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_midline" if is_intermediate else "midline"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо середню лінію m",
            r"m = \frac{a + b}{2}",
            fr"m = \frac{{ {self.a} + {self.b} }}{{ 2 }}",
            self.plot_m,
            rule="Середня лінія трапеції дорівнює півсумі її основ.",
            is_intermediate=is_intermediate
        )
        self.step_num += 1
        self.midline_step_added = True
        return self.plot_m

    def add_isosceles_projection_step(self) -> None:
        if self.projection_step_added:
            return

        diff = self.compute_half_base_difference()
        self.add_step(
            f"Крок {self.step_num}. (Проміжний крок) Проекція бічної сторони",
            r"x = \frac{|a - b|}{2}",
            fr"x = \frac{{ |{self.a} - {self.b}| }}{{ 2 }}",
            diff,
            rule="У рівнобічній трапеції проекція бічної сторони дорівнює піврізниці основ.",
            is_intermediate=True
        )
        self.step_num += 1
        self.projection_step_added = True

    def add_isosceles_height_result(self, result: dict, is_intermediate: bool) -> float:
        if self.height_step_added:
            return self.plot_h

        diff = self.compute_half_base_difference()
        prefix = "(Проміжний крок) " if is_intermediate else ""
        key = "intermediate_height" if is_intermediate else "height"
        result[key] = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо висоту h",
            r"h = \sqrt{c^2 - x^2}",
            fr"h = \sqrt{{ {self.c}^2 - {diff:.2f}^2 }}",
            self.plot_h,
            rule="Знаходимо висоту за теоремою Піфагора з прямокутного трикутника.",
            is_intermediate=is_intermediate
        )
        self.step_num += 1
        self.height_step_added = True
        return self.plot_h

    def add_right_slanted_side_step(self) -> float:
        if self.right_slanted_side_step_added:
            return self.compute_right_slanted_side()

        diff = abs(self.a - self.b)
        c2_val = self.compute_right_slanted_side()
        self.add_step(
            f"Крок {self.step_num}. (Проміжний крок) Знаходимо похилу бічну сторону",
            r"c_{\text{похила}} = \sqrt{h^2 + |a-b|^2}",  # Тут r-рядок, дужки звичайні
            fr"c_{{\text{{похила}}}} = \sqrt{{ {self.h}^2 + {diff}^2 }}",  # Тут f-рядок, дужки подвійні
            c2_val,
            rule="У прямокутній трапеції похила сторона утворює прямокутний трикутник з висотою та різницею основ.",
            is_intermediate=True
        )
        self.step_num += 1
        self.right_slanted_side_step_added = True
        return c2_val

    def _prepare(self) -> None:
        self.task.prepare(self, self._result)
        self.task.add_prerequisites(self, self._result)

    def _generate_image(self) -> str:
        draw_m = self.is_target("midline") or self.task_type == "TRAPEZOID_MIDLINE_HEIGHT"

        return TrapezoidPlotter(
            self.plot_a,
            self.plot_b,
            self.plot_h,
            m=self.plot_m,
            c=self.plot_c if self.plot_type == "isosceles" else None,
            trap_type=self.plot_type,
            draw_m=draw_m,
            r_in=self._result.get("incircle"),
            r_circ=self._result.get("circumcircle")
        ).plot()
