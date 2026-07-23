import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.analytic.entities import Point2D, Vector2D, Line2D
from core.analytic.plotters.analytic_plotter import AnalyticPlotter
from core.analytic.line_formatting import (
    fmt_num, format_linear_expr, format_line_lhs, simplify_line_coefficients,
)


# ============================================================
# 1. Дві точки: відстань, середина, рівняння прямої, нахил
# ============================================================

class TwoPointsTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "TwoPointsSolver") -> bool:
        pass


class GivenTwoPointsTask(TwoPointsTask):
    task_type = "TWO_POINTS"

    def validate(self, solver: "TwoPointsSolver") -> bool:
        if math.isclose(solver.p1.x, solver.p2.x) and math.isclose(solver.p1.y, solver.p2.y):
            solver.add_error("Точки A і B мають бути різними.")
            return False
        return True


class TwoPointsTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "TwoPointsSolver", result: dict) -> None:
        pass


class DistanceTarget(TwoPointsTarget):
    target_name = "distance"

    def calculate(self, solver: "TwoPointsSolver", result: dict) -> None:
        d = solver.p1.distance_to(solver.p2)
        result["distance"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо відстань між точками A і B",
            r"d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}",
            fr"d = \sqrt{{({solver.p2.x} - {solver.p1.x})^2 + ({solver.p2.y} - {solver.p1.y})^2}}",
            d,
            rule="Відстань між двома точками на площині обчислюється як наслідок теореми Піфагора.",
        )
        solver.step_num += 1


class MidpointTarget(TwoPointsTarget):
    target_name = "midpoint"

    def calculate(self, solver: "TwoPointsSolver", result: dict) -> None:
        m = solver.p1.midpoint_with(solver.p2)
        result["midpoint_x"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо координату x середини відрізка",
            r"x_m = \frac{x_1 + x_2}{2}",
            fr"x_m = \frac{{{solver.p1.x} + {solver.p2.x}}}{{2}}",
            m.x,
            rule="Координати середини відрізка дорівнюють півсумі координат його кінців.",
        )
        solver.step_num += 1
        result["midpoint_y"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо координату y середини відрізка",
            r"y_m = \frac{y_1 + y_2}{2}",
            fr"y_m = \frac{{{solver.p1.y} + {solver.p2.y}}}{{2}}",
            m.y,
        )
        solver.step_num += 1


class LineEquationTarget(TwoPointsTarget):
    target_name = "line_equation"

    def calculate(self, solver: "TwoPointsSolver", result: dict) -> None:
        x1, y1 = solver.p1.x, solver.p1.y
        x2, y2 = solver.p2.x, solver.p2.y
        dx, dy = x2 - x1, y2 - y1

        # Розкриваємо (y - y1)(x2 - x1) = (x - x1)(y2 - y1) у стандартну форму Ax + By + C = 0
        a_coef, b_coef, c_coef = -dy, dx, dy * x1 - dx * y1

        raw_lhs = format_line_lhs(a_coef, b_coef, c_coef)
        a_s, b_s, c_s = simplify_line_coefficients(a_coef, b_coef, c_coef)
        simplified_lhs = format_line_lhs(a_s, b_s, c_s)
        simplified_equation = f"{simplified_lhs} = 0"

        x1s, y1s, x2s, y2s = fmt_num(x1), fmt_num(y1), fmt_num(x2), fmt_num(y2)
        dx_s, dy_s = fmt_num(dx), fmt_num(dy)

        derivation_lines = [
            fr"(y - {y1s})({x2s} - {x1s}) = (x - {x1s})({y2s} - {y1s})",
            fr"(y - {y1s}) \cdot {dx_s} = (x - {x1s}) \cdot {dy_s}",
            fr"{format_linear_expr(dx, 'y', -dx * y1)} = {format_linear_expr(dy, 'x', -dy * x1)}",
        ]
        if raw_lhs != simplified_lhs:
            derivation_lines.append(fr"{raw_lhs} = 0")

        derivation_lines.append(fr"\boxed{{{simplified_lhs} = 0}}")

        solution_block = r"\begin{gathered}" + r" \\ ".join(derivation_lines) + r"\end{gathered}"

        result["line_equation"] = simplified_equation
        solver.add_step(
            f"Крок {solver.step_num}. Складаємо рівняння прямої через точки A і B",
            r"(y - y_1)(x_2 - x_1) = (x - x_1)(y_2 - y_1)",
            solution_block,
            simplified_equation,
            rule="Загальне рівняння прямої, що проходить через дві задані точки.",
            show_result_suffix=False,
        )
        solver.step_num += 1


class SlopeTarget(TwoPointsTarget):
    target_name = "slope"

    def calculate(self, solver: "TwoPointsSolver", result: dict) -> None:
        if math.isclose(solver.p2.x, solver.p1.x):
            solver.add_info("Пряма вертикальна — кутовий коефіцієнт не визначений.")
            return
        k = (solver.p2.y - solver.p1.y) / (solver.p2.x - solver.p1.x)
        result["slope"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кутовий коефіцієнт прямої",
            r"k = \frac{y_2 - y_1}{x_2 - x_1}",
            fr"k = \frac{{{solver.p2.y} - {solver.p1.y}}}{{{solver.p2.x} - {solver.p1.x}}}",
            k,
            rule="Кутовий коефіцієнт дорівнює тангенсу кута нахилу прямої до осі Ox.",
        )
        solver.step_num += 1


class TwoPointsSolver(GeometricSolver):
    """Розв'язувач задач про дві точки на площині: відстань, середина, рівняння прямої."""

    TASKS: ClassVar[dict[str, TwoPointsTask]] = {
        task.task_type: task for task in (GivenTwoPointsTask(),)
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, TwoPointsTarget]] = {
        target.target_name: target
        for target in (DistanceTarget(), MidpointTarget(), LineEquationTarget(), SlopeTarget())
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("distance", "midpoint", "line_equation", "slope")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.p1 = Point2D(float(params.get("x1", 0)), float(params.get("y1", 0)))
        self.p2 = Point2D(float(params.get("x2", 0)), float(params.get("y2", 0)))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для точок: {self.task_type}")
            return False
        return self.task.validate(self)

    def line(self) -> Line2D:
        if "line" not in self._computed:
            self._computed["line"] = Line2D.from_two_points(self.p1, self.p2)
        return self._computed["line"]

    def _prepare(self) -> None:
        self.add_info(f"Дано точки A({self.p1.x}, {self.p1.y}) і B({self.p2.x}, {self.p2.y})")

    def _generate_image(self) -> str:
        show_line = self.is_target("line_equation") or self.is_target("slope")
        points = [(self.p1.x, self.p1.y, "A"), (self.p2.x, self.p2.y, "B")]

        if self.is_target("midpoint"):
            m = self.p1.midpoint_with(self.p2)
            points.append((m.x, m.y, "M"))

        lines = []
        if show_line:
            line = self.line()
            lines.append((line.a, line.b, line.c, "AB", "steelblue"))

        return AnalyticPlotter(points=points, lines=lines).plot()


# ============================================================
# 2. Точка і пряма: відстань, основа перпендикуляра
# ============================================================

class PointLineTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "PointLineSolver") -> bool:
        pass


class GivenPointAndLineTask(PointLineTask):
    task_type = "POINT_LINE_DISTANCE"

    def validate(self, solver: "PointLineSolver") -> bool:
        if math.isclose(solver.l1.x, solver.l2.x) and math.isclose(solver.l1.y, solver.l2.y):
            solver.add_error("Пряма має бути задана двома різними точками.")
            return False
        return True


class PointLineTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "PointLineSolver", result: dict) -> None:
        pass


class PointLineDistanceTarget(PointLineTarget):
    target_name = "distance"

    def calculate(self, solver: "PointLineSolver", result: dict) -> None:
        line = solver.line()
        d = line.distance_to_point(solver.point)
        result["distance"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо відстань від точки M до прямої",
            r"d = \frac{|Ax_0 + By_0 + C|}{\sqrt{A^2 + B^2}}",
            fr"d = \frac{{|{line.a:.2f} \cdot {solver.point.x} + {line.b:.2f} \cdot {solver.point.y} + {line.c:.2f}|}}{{\sqrt{{{line.a:.2f}^2 + {line.b:.2f}^2}}}}",
            d,
            rule="Відстань від точки до прямої, заданої загальним рівнянням Ax + By + C = 0.",
        )
        solver.step_num += 1


class FootOfPerpendicularTarget(PointLineTarget):
    target_name = "foot_of_perpendicular"

    def calculate(self, solver: "PointLineSolver", result: dict) -> None:
        line = solver.line()
        a, b, c = line.a, line.b, line.c
        factor = (a * solver.point.x + b * solver.point.y + c) / (a ** 2 + b ** 2)
        foot_x = solver.point.x - a * factor
        foot_y = solver.point.y - b * factor
        result["foot_x"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо координату x основи перпендикуляра",
            r"x_H = x_0 - A \cdot \frac{Ax_0 + By_0 + C}{A^2 + B^2}",
            fr"x_H \approx {foot_x:.2f}",
            foot_x,
            rule="Основа перпендикуляра — точка проєкції M на пряму.",
        )
        solver.step_num += 1
        result["foot_y"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо координату y основи перпендикуляра",
            r"y_H = y_0 - B \cdot \frac{Ax_0 + By_0 + C}{A^2 + B^2}",
            fr"y_H \approx {foot_y:.2f}",
            foot_y,
        )
        solver.step_num += 1


class PointLineSolver(GeometricSolver):
    """Розв'язувач задач про точку і пряму на площині."""

    TASKS: ClassVar[dict[str, PointLineTask]] = {
        task.task_type: task for task in (GivenPointAndLineTask(),)
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, PointLineTarget]] = {
        target.target_name: target
        for target in (PointLineDistanceTarget(), FootOfPerpendicularTarget())
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("distance", "foot_of_perpendicular")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.point = Point2D(float(params.get("px", 0)), float(params.get("py", 0)))
        self.l1 = Point2D(float(params.get("x1", 0)), float(params.get("y1", 0)))
        self.l2 = Point2D(float(params.get("x2", 0)), float(params.get("y2", 0)))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для точки і прямої: {self.task_type}")
            return False
        return self.task.validate(self)

    def line(self) -> Line2D:
        if "line" not in self._computed:
            self._computed["line"] = Line2D.from_two_points(self.l1, self.l2)
        return self._computed["line"]

    def _prepare(self) -> None:
        self.add_info(
            f"Дано точку M({self.point.x}, {self.point.y}) і пряму через "
            f"({self.l1.x}, {self.l1.y}) та ({self.l2.x}, {self.l2.y})"
        )

    def _generate_image(self) -> str:
        line = self.line()
        # Обчислюємо координати основи перпендикуляра для графіка
        a, b, c = line.a, line.b, line.c
        factor = (a * self.point.x + b * self.point.y + c) / (a ** 2 + b ** 2)
        hx = self.point.x - a * factor
        hy = self.point.y - b * factor

        return AnalyticPlotter(
            points=[
                (self.point.x, self.point.y, "M"),
                (hx, hy, "H"),
                # Додаємо точки прямої без підпису, щоб графік правильно взяв межі (bounds)
                (self.l1.x, self.l1.y, ""),
                (self.l2.x, self.l2.y, "")
            ],
            lines=[(line.a, line.b, line.c, "l", "steelblue")],
            segments=[(self.point.x, self.point.y, hx, hy, "indianred", "--")],
            # Малюємо кут 90°. Вектор 1 - це HM, вектор 2 - напрямок прямої
            angles=[(hx, hy, self.point.x - hx, self.point.y - hy, -b, a, r"90^\circ", True)]
        ).plot()


# ============================================================
# 3. Дві прямі: взаємне розташування, перетин, кут
#    (тут — "вузол прийняття рішення" для Activity diagram)
# ============================================================

class TwoLinesTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "TwoLinesSolver") -> bool:
        pass


class GivenTwoLinesTask(TwoLinesTask):
    task_type = "TWO_LINES"

    def validate(self, solver: "TwoLinesSolver") -> bool:
        for p1, p2, name in ((solver.a1, solver.a2, "1"), (solver.b1, solver.b2, "2")):
            if math.isclose(p1.x, p2.x) and math.isclose(p1.y, p2.y):
                solver.add_error(f"Пряма {name} має бути задана двома різними точками.")
                return False
        return True


class TwoLinesTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "TwoLinesSolver", result: dict) -> None:
        pass


class RelationTarget(TwoLinesTarget):
    """
    Визначає взаємне розташування прямих. Це та сама точка розгалуження,
    від якої залежить, чи має сенс далі шукати перетин (IntersectionTarget) —
    саме її варто зобразити як decision-вузол в Activity diagram.
    """
    target_name = "relation"

    def calculate(self, solver: "TwoLinesSolver", result: dict) -> None:
        l1, l2 = solver.line1(), solver.line2()
        solver.add_header(f"Крок {solver.step_num}. Визначаємо взаємне розташування прямих")
        solver.step_num += 1

        if l1.is_parallel_to(l2):
            solver.add_info("Прямі ПАРАЛЕЛЬНІ (напрямні вектори колінеарні).")
            solver.add_rule("Дві прямі паралельні, якщо їхні напрямні (або нормальні) вектори колінеарні.")
            result["relation"] = "Паралельні"
        elif l1.is_perpendicular_to(l2):
            solver.add_info("Прямі ПЕРПЕНДИКУЛЯРНІ (добуток напрямних векторів дорівнює нулю).")
            solver.add_rule("Дві прямі перпендикулярні, якщо скалярний добуток їхніх напрямних векторів дорівнює нулю.")
            result["relation"] = "Перпендикулярні"
        else:
            solver.add_info("Прямі перетинаються під довільним кутом.")
            result["relation"] = "Перетинаються"


class IntersectionTarget(TwoLinesTarget):
    target_name = "intersection"

    def calculate(self, solver: "TwoLinesSolver", result: dict) -> None:
        l1, l2 = solver.line1(), solver.line2()

        if l1.is_parallel_to(l2):
            solver.add_info("Точку перетину знайти неможливо — прямі паралельні.")
            result["intersection"] = "Немає (прямі паралельні)"
            return

        point = l1.intersection_with(l2)
        result["intersection_x"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо координату x точки перетину",
            r"x = \frac{-C_1 B_2 + C_2 B_1}{A_1 B_2 - A_2 B_1}",
            fr"x \approx {point.x:.2f}",
            point.x,
            rule="Точка перетину знаходиться як розв'язок системи двох лінійних рівнянь.",
        )
        solver.step_num += 1
        result["intersection_y"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо координату y точки перетину",
            r"y = \frac{-A_1 C_2 + A_2 C_1}{A_1 B_2 - A_2 B_1}",
            fr"y \approx {point.y:.2f}",
            point.y,
        )
        solver.step_num += 1


class AngleBetweenLinesTarget(TwoLinesTarget):
    target_name = "angle"

    def calculate(self, solver: "TwoLinesSolver", result: dict) -> None:
        l1, l2 = solver.line1(), solver.line2()
        angle = l1.angle_with(l2)
        result["angle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо гострий кут між прямими",
            r"\cos(\varphi) = \frac{|A_1 A_2 + B_1 B_2|}{\sqrt{A_1^2+B_1^2}\sqrt{A_2^2+B_2^2}}",
            fr"\varphi \approx {angle:.2f}^\circ",
            angle,
            rule="Кут між прямими обчислюється через косинус кута між їхніми напрямними векторами.",
        )
        solver.step_num += 1


class TwoLinesSolver(GeometricSolver):
    """Розв'язувач задач про дві прямі, кожна задана парою точок."""

    TASKS: ClassVar[dict[str, TwoLinesTask]] = {
        task.task_type: task for task in (GivenTwoLinesTask(),)
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, TwoLinesTarget]] = {
        target.target_name: target
        for target in (RelationTarget(), IntersectionTarget(), AngleBetweenLinesTarget())
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("relation", "intersection", "angle")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a1 = Point2D(float(params.get("x1", 0)), float(params.get("y1", 0)))
        self.a2 = Point2D(float(params.get("x2", 0)), float(params.get("y2", 0)))
        self.b1 = Point2D(float(params.get("x3", 0)), float(params.get("y3", 0)))
        self.b2 = Point2D(float(params.get("x4", 0)), float(params.get("y4", 0)))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для двох прямих: {self.task_type}")
            return False
        return self.task.validate(self)

    def line1(self) -> Line2D:
        if "line1" not in self._computed:
            self._computed["line1"] = Line2D.from_two_points(self.a1, self.a2)
        return self._computed["line1"]

    def line2(self) -> Line2D:
        if "line2" not in self._computed:
            self._computed["line2"] = Line2D.from_two_points(self.b1, self.b2)
        return self._computed["line2"]

    def _prepare(self) -> None:
        self.add_info(
            f"Пряма 1 через ({self.a1.x}, {self.a1.y}) і ({self.a2.x}, {self.a2.y}); "
            f"пряма 2 через ({self.b1.x}, {self.b1.y}) і ({self.b2.x}, {self.b2.y})"
        )

    def _generate_image(self) -> str:
        l1, l2 = self.line1(), self.line2()

        # Додаємо невидимі базові точки для правильного розрахунку масштабу
        points = [
            (self.a1.x, self.a1.y, ""), (self.a2.x, self.a2.y, ""),
            (self.b1.x, self.b1.y, ""), (self.b2.x, self.b2.y, "")
        ]
        angles = []

        pt = l1.intersection_with(l2)
        if pt:
            points.append((pt.x, pt.y, "P"))
            angle_deg = l1.angle_with(l2)
            is_right = math.isclose(angle_deg, 90, abs_tol=1e-3)

            # Вектори напрямку прямих
            v1, v2 = l1.direction_vector(), l2.direction_vector()
            # Обертаємо вектор, якщо він вказує на тупий кут, щоб намалювати саме гострий
            if v1.dot(v2) < 0:
                v2 = __import__("core.analytic.entities", fromlist=["Vector2D"]).Vector2D(-v2.x, -v2.y)

            angles.append((pt.x, pt.y, v1.x, v1.y, v2.x, v2.y, fr"{angle_deg:.1f}^\circ", is_right))

        return AnalyticPlotter(
            points=points,
            lines=[
                (l1.a, l1.b, l1.c, "l1", "steelblue"),
                (l2.a, l2.b, l2.c, "l2", "indianred"),
            ],
            angles=angles
        ).plot()


# ============================================================
# 4. Вектори: довжина, скалярний добуток, кут, перпендикулярність
# ============================================================

class VectorsTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "VectorsSolver") -> bool:
        pass


class GivenTwoVectorsTask(VectorsTask):
    task_type = "VECTORS"

    def validate(self, solver: "VectorsSolver") -> bool:
        if solver.v1.magnitude() == 0 or solver.v2.magnitude() == 0:
            solver.add_error("Вектори мають бути ненульовими.")
            return False
        return True


class VectorsTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "VectorsSolver", result: dict) -> None:
        pass


class MagnitudeTarget(VectorsTarget):
    target_name = "magnitude"

    def calculate(self, solver: "VectorsSolver", result: dict) -> None:
        result["magnitude_1"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо довжину вектора a",
            r"|\vec{a}| = \sqrt{x^2 + y^2}",
            fr"|\vec{{a}}| = \sqrt{{{solver.v1.x}^2 + {solver.v1.y}^2}}",
            solver.v1.magnitude(),
        )
        solver.step_num += 1
        result["magnitude_2"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо довжину вектора b",
            r"|\vec{b}| = \sqrt{x^2 + y^2}",
            fr"|\vec{{b}}| = \sqrt{{{solver.v2.x}^2 + {solver.v2.y}^2}}",
            solver.v2.magnitude(),
        )
        solver.step_num += 1


class DotProductTarget(VectorsTarget):
    target_name = "dot_product"

    def calculate(self, solver: "VectorsSolver", result: dict) -> None:
        dot = solver.v1.dot(solver.v2)
        result["dot_product"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо скалярний добуток векторів",
            r"\vec{a} \cdot \vec{b} = x_1 x_2 + y_1 y_2",
            fr"\vec{{a}} \cdot \vec{{b}} = {solver.v1.x} \cdot {solver.v2.x} + {solver.v1.y} \cdot {solver.v2.y}",
            dot,
            rule="Скалярний добуток дорівнює сумі добутків відповідних координат векторів.",
        )
        solver.step_num += 1


class AngleBetweenVectorsTarget(VectorsTarget):
    target_name = "angle"

    def calculate(self, solver: "VectorsSolver", result: dict) -> None:
        angle = solver.v1.angle_with(solver.v2)
        result["angle"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо кут між векторами",
            r"\cos(\varphi) = \frac{\vec{a} \cdot \vec{b}}{|\vec{a}| \cdot |\vec{b}|}",
            fr"\varphi \approx {angle:.2f}^\circ",
            angle,
            rule="Кут між векторами обчислюється через косинус, виражений зі скалярного добутку.",
        )
        solver.step_num += 1


class IsPerpendicularTarget(VectorsTarget):
    target_name = "is_perpendicular"

    def calculate(self, solver: "VectorsSolver", result: dict) -> None:
        perpendicular = solver.v1.is_perpendicular_to(solver.v2)
        result["is_perpendicular"] = "Так" if perpendicular else "Ні"
        solver.add_info(
            "Вектори перпендикулярні (скалярний добуток дорівнює нулю)."
            if perpendicular else
            "Вектори не перпендикулярні (скалярний добуток не дорівнює нулю)."
        )


class VectorsSolver(GeometricSolver):
    """Розв'язувач задач про вектори на площині."""

    TASKS: ClassVar[dict[str, VectorsTask]] = {
        task.task_type: task for task in (GivenTwoVectorsTask(),)
    }
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, VectorsTarget]] = {
        target.target_name: target
        for target in (MagnitudeTarget(), DotProductTarget(), AngleBetweenVectorsTarget(), IsPerpendicularTarget())
    }
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ("magnitude", "dot_product", "angle", "is_perpendicular")

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.v1 = Vector2D(float(params.get("x1", 0)), float(params.get("y1", 0)))
        self.v2 = Vector2D(float(params.get("x2", 0)), float(params.get("y2", 0)))

    def validate(self) -> bool:
        if self.task is None:
            self.add_error(f"Невідомий тип задачі для векторів: {self.task_type}")
            return False
        return self.task.validate(self)

    def _prepare(self) -> None:
        self.add_info(f"Дано вектори a({self.v1.x}, {self.v1.y}) і b({self.v2.x}, {self.v2.y})")

    def _generate_image(self) -> str:
        angle_deg = self.v1.angle_with(self.v2)
        is_right = math.isclose(angle_deg, 90, abs_tol=1e-3)
        return AnalyticPlotter(
            vectors=[
                (0, 0, self.v1.x, self.v1.y, "a", "steelblue"),
                (0, 0, self.v2.x, self.v2.y, "b", "indianred"),
            ],
            angles=[(0, 0, self.v1.x, self.v1.y, self.v2.x, self.v2.y, fr"{angle_deg:.1f}^\circ", is_right)]
        ).plot()