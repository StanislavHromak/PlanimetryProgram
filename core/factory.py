from core.base import GeometricSolver
from core.interfaces import Solver, SolverCreator

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
    """Фабрика реєстрації солверів."""

    _registry: dict[tuple[str, str], SolverCreator] = {}

    @classmethod
    def register(cls, figure: str, task_type: str, creator: SolverCreator) -> None:
        cls._registry[(figure, task_type)] = creator

    @classmethod
    def register_solver(
        cls,
        figure: str,
        solver_cls: type[GeometricSolver],
        creator: SolverCreator | None = None,
    ) -> None:
        solver_creator = creator or solver_cls
        for task_type in solver_cls.supported_tasks():
            cls.register(figure, task_type, solver_creator)

    @classmethod
    def create_solver(
        cls,
        figure: str,
        task_type: str,
        params: dict,
        targets: list,
    ) -> Solver:
        creator = cls._registry.get((figure, task_type))
        if creator is None:
            raise ValueError(
                f"Фабрика не знає як створити: фігура '{figure}', "
                f"тип задачі '{task_type}'"
            )

        return creator(task_type, params, targets)


def _create_regular_polygon(task_type: str, params: dict, targets: list) -> Solver:
    n = params.get("n", 3)
    return RegularPolygonSolver(n, task_type, params, targets)


def _register_solvers() -> None:
    GeometryFactory.register_solver("regular_polygon", RegularPolygonSolver, _create_regular_polygon)

    GeometryFactory.register_solver("triangle", ArbitraryTriangleSolver)
    GeometryFactory.register_solver("triangle", RightTriangleSolver)
    GeometryFactory.register_solver("triangle", IsoscelesTriangleSolver)
    GeometryFactory.register_solver("triangle", EquilateralTriangleSolver)

    GeometryFactory.register_solver("quadrangle", ArbitraryQuadrangleSolver)
    GeometryFactory.register_solver("quadrangle", SquareSolver)
    GeometryFactory.register_solver("quadrangle", RectangleSolver)
    GeometryFactory.register_solver("quadrangle", RhombusSolver)
    GeometryFactory.register_solver("quadrangle", ParallelogramSolver)
    GeometryFactory.register_solver("quadrangle", TrapezoidSolver)

    GeometryFactory.register_solver("curves", CircleSolver)
    GeometryFactory.register_solver("curves", SectorSolver)
    GeometryFactory.register_solver("curves", EllipseSolver)


_register_solvers()
