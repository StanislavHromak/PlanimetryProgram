import math

import pytest

from core.polygons.quadrangles.rectangle import RectangleSolver


class TestRectangleSolver:
    def test_sides_given_finds_area_and_perimeter(self):
        solver = RectangleSolver(
            task_type="RECTANGLE_SIDES",
            params={"a": 3, "b": 4},
            targets=["area", "perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(12)
        assert result["data"]["perimeter"] == pytest.approx(14)

    def test_area_and_side_finds_other_side(self):
        solver = RectangleSolver(
            task_type="RECTANGLE_AREA_SIDE",
            params={"a": 4, "S": 20},
            targets=["side_b"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_b"] == pytest.approx(5)

    def test_diagonal_and_side_finds_other_side(self):
        solver = RectangleSolver(
            task_type="RECTANGLE_DIAGONAL_SIDE",
            params={"a": 3, "d": 5},
            targets=["side_b"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_b"] == pytest.approx(4)

    @pytest.mark.parametrize("task_type, params", [
        ("RECTANGLE_SIDES", {"a": 0, "b": 4}),
        ("RECTANGLE_PERIMETER_SIDE", {"a": 5, "P": 8}),
        ("RECTANGLE_DIAGONAL_SIDE", {"a": 5, "d": 3}),
    ])
    def test_invalid_input_fails_validation(self, task_type, params):
        solver = RectangleSolver(task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()
        assert result["success"] is False
