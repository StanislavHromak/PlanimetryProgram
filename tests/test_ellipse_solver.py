import math

import pytest

from core.curves.ellipse import EllipseSolver


class TestEllipseSolver:
    def test_axes_given_finds_area_and_eccentricity(self):
        solver = EllipseSolver(
            task_type="ELLIPSE_AXES",
            params={"a": 5, "b": 3},
            targets=["area", "eccentricity"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(math.pi * 15, rel=0.01)
        assert result["data"]["eccentricity"] == pytest.approx(0.8, rel=0.01)

    @pytest.mark.parametrize("params", [
        {"a": 0, "b": 3},
        {"a": 5, "b": -1},
    ])
    def test_non_positive_axes_fail_validation(self, params):
        solver = EllipseSolver(
            task_type="ELLIPSE_AXES",
            params=params,
            targets=["area"],
        )
        result = solver.calculate()
        assert result["success"] is False
