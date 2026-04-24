from core.curves.circle import CircleSolver
from core.curves.sector import SectorSolver
from core.curves.ellipse import EllipseSolver

from core.polygons.regular.regular import RegularPolygonSolver

from core.polygons.triangles.arbitrary_triangle import ArbitraryTriangleSolver
from core.polygons.triangles.right_triangle import RightTriangleSolver
from core.polygons.triangles.isosceles_triangle import IsoscelesTriangleSolver
from core.polygons.triangles.equilateral_triangle import EquilateralTriangleSolver

from core.polygons.quadrangles.arbitrary_quadrangle import ArbitraryQuadrangleSolver
from core.polygons.quadrangles.parallelogram import ParallelogramSolver
from core.polygons.quadrangles.rectangle import RectangleSolver
from core.polygons.quadrangles.rhombus import RhombusSolver
from core.polygons.quadrangles.square import SquareSolver
from core.polygons.quadrangles.trapezoid import TrapezoidSolver

class GeometryFactory:
    """Патерн Factory Method для створення правильного об'єкта-розв'язувача."""

    @staticmethod
    def create_solver(figure: str, task_type: str, params: dict, targets: list):

        # --- БЛОК БАГАТОКУТНИКІВ ---
        if figure == "regular_polygon":
            n = params.get('n', 3)
            return RegularPolygonSolver(n, task_type, params, targets)

        # --- БЛОК ТРИКУТНИКІВ ---
        elif figure == "triangle":
            if task_type in ["SSS", "SAS", "ASA"]:
                return ArbitraryTriangleSolver(task_type, params, targets)

            elif task_type in ["RIGHT_LEGS", "RIGHT_LEG_HYPOTENUSE"]:
                return RightTriangleSolver(task_type, params, targets)

            elif task_type == "ISOSCELES_BASE_SIDE":
                return IsoscelesTriangleSolver(task_type, params, targets)

            elif task_type == "EQUILATERAL_SIDE":
                return EquilateralTriangleSolver(task_type, params, targets)

        # --- БЛОК ЧОТИРИКУТНИКІВ ---
        elif figure == "quadrangle":
            if task_type == "ARB_SIDES_ANGLES":
                return ArbitraryQuadrangleSolver(task_type, params, targets)
            elif task_type in ["SQUARE_SIDE", "SQUARE_AREA", "SQUARE_PERIMETER", "SQUARE_DIAGONAL"]:
                return SquareSolver(task_type, params, targets)
            elif task_type in ["RECTANGLE_SIDES", "RECTANGLE_AREA_SIDE", "RECTANGLE_PERIMETER_SIDE",
                               "RECTANGLE_DIAGONAL_SIDE"]:
                return RectangleSolver(task_type, params, targets)
            elif task_type in ["RHOMBUS_DIAGONALS", "RHOMBUS_SIDE_ANGLE", "RHOMBUS_AREA_SIDE",
                               "RHOMBUS_DIAGONAL_SIDE"]:
                return RhombusSolver(task_type, params, targets)
            elif task_type in ["PARALLELOGRAM_S_A", "PARALLELOGRAM_D_A"]:
                return ParallelogramSolver(task_type, params, targets)
            elif task_type in ["TRAPEZOID_ABH", "TRAPEZOID_AREA_BASES", "TRAPEZOID_MIDLINE_HEIGHT",
                               "ISOSCELES_TRAPEZOID_BASES_LEG"]:
                return TrapezoidSolver(task_type, params, targets)

        # --- БЛОК КРИВОЛІНІЙНИХ ФІГУР ---
        elif figure == "curves":
            if task_type in ["CIRCLE_RADIUS", "CIRCLE_DIAMETER", "CIRCLE_CIRCUMFERENCE", "CIRCLE_AREA"]:
                return CircleSolver(task_type, params, targets)
            elif task_type == "SECTOR_AND_ARC":
                return SectorSolver(task_type, params, targets)
            elif task_type == "ELLIPSE_AXES":
                return EllipseSolver(task_type, params, targets)

        # Якщо нічого не підійшло
        raise ValueError(f"Фабрика не знає як створити: фігура '{figure}', тип задачі '{task_type}'")