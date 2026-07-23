import pytest

from core.analytic.analytic_geometry import (
    TwoPointsSolver,
    PointLineSolver,
    TwoLinesSolver,
    VectorsSolver,
)


class TestTwoPointsSolver:
    def test_distance_and_midpoint(self):
        solver = TwoPointsSolver(
            task_type="TWO_POINTS",
            params={"x1": 0, "y1": 0, "x2": 3, "y2": 4},
            targets=["distance", "midpoint"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["distance"] == pytest.approx(5)
        assert result["data"]["midpoint_x"] == pytest.approx(1.5)
        assert result["data"]["midpoint_y"] == pytest.approx(2)

    def test_slope(self):
        solver = TwoPointsSolver(
            task_type="TWO_POINTS",
            params={"x1": 0, "y1": 0, "x2": 2, "y2": 4},
            targets=["slope"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["slope"] == pytest.approx(2)

    def test_vertical_line_has_no_slope(self):
        solver = TwoPointsSolver(
            task_type="TWO_POINTS",
            params={"x1": 1, "y1": 0, "x2": 1, "y2": 5},
            targets=["slope"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert "slope" not in result["data"]

    def test_line_equation(self):
        solver = TwoPointsSolver(
            task_type="TWO_POINTS",
            params={"x1": 0, "y1": 0, "x2": 2, "y2": 2},
            targets=["line_equation"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["line_equation"] == "x - y = 0"

    def test_identical_points_fail_validation(self):
        solver = TwoPointsSolver(
            task_type="TWO_POINTS",
            params={"x1": 1, "y1": 1, "x2": 1, "y2": 1},
            targets=["distance"],
        )
        result = solver.calculate()

        assert result["success"] is False
        assert "різними" in result["error"].lower()


class TestPointLineSolver:
    def test_distance_to_vertical_line(self):
        solver = PointLineSolver(
            task_type="POINT_LINE_DISTANCE",
            params={"px": 0, "py": 0, "x1": 1, "y1": 0, "x2": 1, "y2": 2},
            targets=["distance"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["distance"] == pytest.approx(1)

    def test_foot_of_perpendicular(self):
        solver = PointLineSolver(
            task_type="POINT_LINE_DISTANCE",
            params={"px": 0, "py": 0, "x1": 1, "y1": 0, "x2": 1, "y2": 2},
            targets=["foot_of_perpendicular"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["foot_x"] == pytest.approx(1)
        assert result["data"]["foot_y"] == pytest.approx(0)

    def test_degenerate_line_fails_validation(self):
        solver = PointLineSolver(
            task_type="POINT_LINE_DISTANCE",
            params={"px": 0, "py": 0, "x1": 2, "y1": 2, "x2": 2, "y2": 2},
            targets=["distance"],
        )
        result = solver.calculate()

        assert result["success"] is False


class TestTwoLinesSolver:
    def test_perpendicular_lines_relation_and_intersection(self):
        solver = TwoLinesSolver(
            task_type="TWO_LINES",
            params={
                "x1": 0, "y1": 0, "x2": 1, "y2": 0,  # x-axis
                "x3": 0, "y3": 0, "x4": 0, "y4": 1,  # y-axis
            },
            targets=["relation", "intersection", "angle"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["relation"] == "Перпендикулярні"
        assert result["data"]["intersection_x"] == pytest.approx(0)
        assert result["data"]["intersection_y"] == pytest.approx(0)
        assert result["data"]["angle"] == pytest.approx(90)

    def test_parallel_lines_have_no_intersection(self):
        solver = TwoLinesSolver(
            task_type="TWO_LINES",
            params={
                "x1": 0, "y1": 0, "x2": 1, "y2": 0,
                "x3": 0, "y3": 1, "x4": 1, "y4": 1,
            },
            targets=["relation", "intersection"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["relation"] == "Паралельні"
        assert result["data"]["intersection"] == "Немає (прямі паралельні)"

    @pytest.mark.parametrize("params", [
        {"x1": 5, "y1": 5, "x2": 5, "y2": 5, "x3": 0, "y3": 0, "x4": 1, "y4": 1},
    ])
    def test_degenerate_line_fails_validation(self, params):
        solver = TwoLinesSolver(task_type="TWO_LINES", params=params, targets=["relation"])
        result = solver.calculate()
        assert result["success"] is False


class TestVectorsSolver:
    def test_perpendicular_unit_vectors(self):
        solver = VectorsSolver(
            task_type="VECTORS",
            params={"x1": 1, "y1": 0, "x2": 0, "y2": 1},
            targets=["magnitude", "dot_product", "angle", "is_perpendicular"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["magnitude_1"] == pytest.approx(1)
        assert result["data"]["magnitude_2"] == pytest.approx(1)
        assert result["data"]["dot_product"] == pytest.approx(0)
        assert result["data"]["angle"] == pytest.approx(90)
        assert result["data"]["is_perpendicular"] == "Так"

    def test_non_perpendicular_vectors(self):
        solver = VectorsSolver(
            task_type="VECTORS",
            params={"x1": 1, "y1": 0, "x2": 1, "y2": 1},
            targets=["is_perpendicular"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["is_perpendicular"] == "Ні"

    def test_zero_vector_fails_validation(self):
        solver = VectorsSolver(
            task_type="VECTORS",
            params={"x1": 0, "y1": 0, "x2": 1, "y2": 1},
            targets=["magnitude"],
        )
        result = solver.calculate()

        assert result["success"] is False
        assert "ненульовими" in result["error"].lower()