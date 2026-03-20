from core.polygons.triangle import TriangleSSSSolver, TriangleSASSolver, TriangleASASolver
from core.curves.circle import CircleSolver, CircleSectorSolver
from core.polygons.quadrangle import (
    SquareSolver,
    RectangleSolver,
    RhombusSolver,
    ParallelogramSolver,
    TrapezoidSolver
)

class GeometryFactory:
    """Паттерн Factory Method для створення правильного об'єкта-розв'язувача."""

    @staticmethod
    def create_solver(figure: str, task_type: str, params: dict, targets: list):

        if figure == "triangle":
            if task_type == "SSS":
                return TriangleSSSSolver(
                    a=params.get('a'), b=params.get('b'), c=params.get('c'), targets=targets
                )
            elif task_type == "SAS":
                return TriangleSASSolver(
                    a=params.get('a'), b=params.get('b'), angle_c=params.get('angle_c'), targets=targets
                )
            elif task_type == "ASA":
                return TriangleASASolver(
                    a=params.get('a'), angle_b=params.get('angle_b'), angle_c=params.get('angle_c'), targets=targets
                )

        elif figure == "quadrangle":
            if task_type == "SQUARE_SIDE":
                return SquareSolver(task_type, params, targets)

            elif task_type == "RECTANGLE_SIDES":
                return RectangleSolver(task_type, params, targets)

            elif task_type in ["RHOMBUS_DIAGONALS", "RHOMBUS_SIDE_ANGLE"]:
                return RhombusSolver(task_type, params, targets)

            elif task_type == "PARALLELOGRAM_S_A":
                return ParallelogramSolver(task_type, params, targets)

            elif task_type == "TRAPEZOID_ABH":
                return TrapezoidSolver(task_type, params, targets)

        elif figure == "circle":
            if task_type == "SECTOR_AND_ARC":
                return CircleSectorSolver(
                    radius=params.get('radius'),
                    angle=params.get('angle'),
                    targets=targets
                )
            # Всі інші типи (RADIUS, DIAMETER, AREA, CIRCUMFERENCE) використовують CircleSolver
            elif task_type in ["RADIUS", "DIAMETER", "CIRCUMFERENCE", "AREA"]:
                return CircleSolver(task_type, params.get(task_type.lower()), targets)

        # Фоллбек для помилок
        raise ValueError(f"Фабрика не знає як створити: фігура '{figure}', тип задачі '{task_type}'")