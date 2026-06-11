import pytest

from core.polygons.triangles.isosceles_triangle import IsoscelesTriangleSolver


class TestIsoscelesTriangleSolver:
    def test_base_and_side_finds_height_area_perimeter(self):
        solver = IsoscelesTriangleSolver(
            task_type="ISOSCELES_BASE_SIDE",
            params={"base": 6, "side": 5},
            targets=["height", "area", "perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["height"] == pytest.approx(4)
        assert result["data"]["area"] == pytest.approx(12)
        assert result["data"]["perimeter"] == pytest.approx(16)

    @pytest.mark.parametrize("params, expected_error", [
        ({"base": 0, "side": 5}, "додатн"),
        ({"base": 12, "side": 5}, "нерівність"),
    ])
    def test_invalid_input_fails_validation(self, params, expected_error):
        solver = IsoscelesTriangleSolver(
            task_type="ISOSCELES_BASE_SIDE",
            params=params,
            targets=["area"],
        )
        result = solver.calculate()

        assert result["success"] is False
        assert expected_error in result["error"].lower()
