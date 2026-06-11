import pytest

from core.factory import GeometryFactory
from core.curves.circle import CircleSolver
from core.curves.sector import SectorSolver
from core.curves.ellipse import EllipseSolver
from core.polygons.regular.regular import RegularPolygonSolver
from core.polygons.triangles.arbitrary_triangle import ArbitraryTriangleSolver
from core.polygons.triangles.right_triangle import RightTriangleSolver
from core.polygons.triangles.isosceles_triangle import IsoscelesTriangleSolver
from core.polygons.triangles.equilateral_triangle import EquilateralTriangleSolver
from core.polygons.quadrangles.arbitrary_quadrangle import ArbitraryQuadrangleSolver
from core.polygons.quadrangles.square import SquareSolver
from core.polygons.quadrangles.rectangle import RectangleSolver
from core.polygons.quadrangles.rhombus import RhombusSolver
from core.polygons.quadrangles.parallelogram import ParallelogramSolver
from core.polygons.quadrangles.trapezoid import TrapezoidSolver


ALL_SOLVERS = [
    ("curves", "CIRCLE_RADIUS", {"radius": 5}, ["area"], CircleSolver),
    ("curves", "SECTOR_AND_ARC", {"radius": 5, "angle": 90}, ["arc_length"], SectorSolver),
    ("curves", "ELLIPSE_AXES", {"a": 5, "b": 3}, ["area"], EllipseSolver),
    ("regular_polygon", "REGULAR_SIDE", {"a": 5, "n": 6}, ["area"], RegularPolygonSolver),
    ("triangle", "SSS", {"a": 3, "b": 4, "c": 5}, ["area"], ArbitraryTriangleSolver),
    ("triangle", "RIGHT_LEGS", {"a": 3, "b": 4}, ["area"], RightTriangleSolver),
    ("triangle", "ISOSCELES_BASE_SIDE", {"base": 6, "side": 5}, ["area"], IsoscelesTriangleSolver),
    ("triangle", "EQUILATERAL_SIDE", {"a": 6}, ["area"], EquilateralTriangleSolver),
    ("quadrangle", "ARB_SIDES_ANGLES", {"a": 3, "b": 4, "c": 3, "d": 4, "angle": 90}, ["area"], ArbitraryQuadrangleSolver),
    ("quadrangle", "SQUARE_SIDE", {"a": 4}, ["area"], SquareSolver),
    ("quadrangle", "RECTANGLE_SIDES", {"a": 3, "b": 4}, ["area"], RectangleSolver),
    ("quadrangle", "RHOMBUS_DIAGONALS", {"d1": 6, "d2": 8}, ["area"], RhombusSolver),
    ("quadrangle", "PARALLELOGRAM_S_A", {"a": 5, "b": 4, "angle": 90}, ["area"], ParallelogramSolver),
    ("quadrangle", "TRAPEZOID_ABH", {"a": 10, "b": 6, "h": 4}, ["area"], TrapezoidSolver),
]


class TestGeometryFactory:
    @pytest.mark.parametrize("figure, task_type, params, targets, solver_cls", ALL_SOLVERS)
    def test_create_all_registered_solvers(self, figure, task_type, params, targets, solver_cls):
        solver = GeometryFactory.create_solver(
            figure=figure,
            task_type=task_type,
            params=params,
            targets=targets,
        )
        assert isinstance(solver, solver_cls)

    def test_unknown_figure_raises_value_error(self):
        with pytest.raises(ValueError, match="Фабрика не знає"):
            GeometryFactory.create_solver(
                figure="unknown",
                task_type="CIRCLE_RADIUS",
                params={"radius": 1},
                targets=[],
            )

    def test_unknown_task_type_fails_on_calculate(self):
        solver = CircleSolver(
            task_type="INVALID_TASK",
            params={"radius": 5},
            targets=["area"],
        )
        result = solver.calculate()
        assert result["success"] is False
        assert "Невідомий тип задачі" in result["error"]
