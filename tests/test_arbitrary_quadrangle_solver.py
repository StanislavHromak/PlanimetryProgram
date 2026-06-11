import pytest

from core.polygons.quadrangles.arbitrary_quadrangle import ArbitraryQuadrangleSolver


class TestArbitraryQuadrangleSolver:
    def test_sides_and_angle_finds_perimeter_and_area(self):
        solver = ArbitraryQuadrangleSolver(
            task_type="ARB_SIDES_ANGLES",
            params={"a": 3, "b": 4, "c": 3, "d": 4, "angle": 90},
            targets=["perimeter", "area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["perimeter"] == pytest.approx(14)
        assert result["data"]["area"] == pytest.approx(12)

    @pytest.mark.parametrize("params", [
        {"a": 0, "b": 4, "c": 3, "d": 4, "angle": 90},
        {"a": 3, "b": 4, "c": 3, "d": 4, "angle": 180},
    ])
    def test_invalid_input_fails_validation(self, params):
        solver = ArbitraryQuadrangleSolver(
            task_type="ARB_SIDES_ANGLES",
            params=params,
            targets=["area"],
        )
        result = solver.calculate()
        assert result["success"] is False
