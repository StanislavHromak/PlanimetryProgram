from core.curves.circle import CircleSolver, CircleSectorSolver

from core.polygons.triangle import (
    ArbitraryTriangleSolver,
    RightTriangleSolver,
    IsoscelesTriangleSolver,
    EquilateralTriangleSolver
)

from core.polygons.quadrangle import (
    SquareSolver,
    RectangleSolver,
    RhombusSolver,
    ParallelogramSolver,
    TrapezoidSolver,
    ArbitraryQuadrangleSolver
)


class GeometryFactory:
    """Патерн Factory Method для створення правильного об'єкта-розв'язувача."""

    @staticmethod
    def create_solver(figure: str, task_type: str, params: dict, targets: list):

        # --- БЛОК ТРИКУТНИКІВ ---
        if figure == "triangle":
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
            elif task_type == "SQUARE_SIDE":
                return SquareSolver(task_type, params, targets)
            elif task_type == "RECTANGLE_SIDES":
                return RectangleSolver(task_type, params, targets)
            elif task_type in ["RHOMBUS_DIAGONALS", "RHOMBUS_SIDE_ANGLE"]:
                return RhombusSolver(task_type, params, targets)
            elif task_type in ["PARALLELOGRAM_S_A", "PARALLELOGRAM_D_A"]:
                return ParallelogramSolver(task_type, params, targets)
            elif task_type == "TRAPEZOID_ABH":
                return TrapezoidSolver(task_type, params, targets)

        # --- БЛОК КІЛ ТА КРУГІВ ---
        elif figure == "circle":
            if task_type == "SECTOR_AND_ARC":
                return CircleSectorSolver(radius=params.get('radius'), angle=params.get('angle'), targets=targets)
            elif task_type in ["RADIUS", "DIAMETER", "CIRCUMFERENCE", "AREA"]:
                return CircleSolver(task_type, params.get(task_type.lower()), targets)

        raise ValueError(f"Фабрика не знає як створити: фігура '{figure}', тип задачі '{task_type}'")