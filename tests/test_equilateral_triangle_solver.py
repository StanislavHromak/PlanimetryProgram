import math

import pytest

from core.polygons.triangles.equilateral_triangle import EquilateralTriangleSolver


class TestEquilateralTriangleSolver:
    def test_side_given_finds_all_targets(self):
        solver = EquilateralTriangleSolver(
            task_type="EQUILATERAL_SIDE",
            params={"a": 6},
            targets=["area", "perimeter", "incircle", "circumcircle"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(9 * math.sqrt(3), rel=0.01)
        assert result["data"]["perimeter"] == pytest.approx(18)
        assert result["data"]["r_inscribed"] == pytest.approx(math.sqrt(3), rel=0.01)
        assert result["data"]["r_circumscribed"] == pytest.approx(2 * math.sqrt(3), rel=0.01)

    def test_non_positive_side_fails_validation(self):
        solver = EquilateralTriangleSolver(
            task_type="EQUILATERAL_SIDE",
            params={"a": 0},
            targets=["area"],
        )
        result = solver.calculate()
        assert result["success"] is False
