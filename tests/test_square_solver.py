import math

import pytest

from core.polygons.quadrangles.square import SquareSolver


class TestSquareSolver:
    def test_side_given_finds_area_and_perimeter(self):
        solver = SquareSolver(
            task_type="SQUARE_SIDE",
            params={"a": 4},
            targets=["area", "perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(16)
        assert result["data"]["perimeter"] == pytest.approx(16)

    def test_area_given_finds_side(self):
        solver = SquareSolver(
            task_type="SQUARE_AREA",
            params={"S": 25},
            targets=["side_a"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_a"] == pytest.approx(5)

    def test_perimeter_given_finds_side(self):
        solver = SquareSolver(
            task_type="SQUARE_PERIMETER",
            params={"P": 20},
            targets=["side_a"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_a"] == pytest.approx(5)

    def test_diagonal_given_finds_side(self):
        solver = SquareSolver(
            task_type="SQUARE_DIAGONAL",
            params={"d": 5 * math.sqrt(2)},
            targets=["side_a"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_a"] == pytest.approx(5)

    def test_side_given_finds_incircle_and_circumcircle(self):
        solver = SquareSolver(
            task_type="SQUARE_SIDE",
            params={"a": 6},
            targets=["incircle", "circumcircle"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["incircle"] == pytest.approx(3)
        assert result["data"]["circumcircle"] == pytest.approx(3 * math.sqrt(2), rel=0.01)

    @pytest.mark.parametrize("task_type, params", [
        ("SQUARE_SIDE", {"a": 0}),
        ("SQUARE_AREA", {"S": -4}),
        ("SQUARE_PERIMETER", {"P": 0}),
        ("SQUARE_DIAGONAL", {"d": -1}),
    ])
    def test_non_positive_input_fails_validation(self, task_type, params):
        solver = SquareSolver(task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()

        assert result["success"] is False
