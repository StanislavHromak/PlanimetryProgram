import math

import pytest

from core.polygons.regular.regular import RegularPolygonSolver


class TestRegularPolygonSolver:
    def test_side_given_finds_area_and_perimeter(self):
        solver = RegularPolygonSolver(
            n=6,
            task_type="REGULAR_SIDE",
            params={"a": 2},
            targets=["area", "perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(6 * math.sqrt(3), rel=0.01)
        assert result["data"]["perimeter"] == pytest.approx(12)

    def test_perimeter_given_finds_side(self):
        solver = RegularPolygonSolver(
            n=5,
            task_type="REGULAR_PERIMETER",
            params={"P": 25},
            targets=["side"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side"] == pytest.approx(5)

    def test_angle_and_side_determines_n(self):
        solver = RegularPolygonSolver(
            n=3,
            task_type="REGULAR_ANGLE_SIDE",
            params={"alpha": 120, "a": 4},
            targets=["perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["n_sides"] == pytest.approx(6)
        assert result["data"]["perimeter"] == pytest.approx(24)

    @pytest.mark.parametrize("n, task_type, params", [
        (3, "REGULAR_SIDE", {"a": 0}),
        (2, "REGULAR_SIDE", {"a": 5}),
        (6, "REGULAR_ANGLE_SIDE", {"alpha": 100, "a": 4}),
    ])
    def test_invalid_input_fails_validation(self, n, task_type, params):
        solver = RegularPolygonSolver(n=n, task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()
        assert result["success"] is False
