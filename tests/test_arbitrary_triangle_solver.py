import math

import pytest

from core.polygons.triangles.arbitrary_triangle import ArbitraryTriangleSolver


class TestArbitraryTriangleSolver:
    def test_sss_finds_perimeter_and_area(self):
        solver = ArbitraryTriangleSolver(
            task_type="SSS",
            params={"a": 3, "b": 4, "c": 5},
            targets=["perimeter", "area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["perimeter"] == pytest.approx(12)
        assert result["data"]["area"] == pytest.approx(6)

    def test_sas_finds_side_c(self):
        solver = ArbitraryTriangleSolver(
            task_type="SAS",
            params={"a": 3, "b": 4, "angle_c": 90},
            targets=["side"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_c"] == pytest.approx(5)

    def test_asa_finds_sides(self):
        solver = ArbitraryTriangleSolver(
            task_type="ASA",
            params={"a": 10, "angle_b": 30, "angle_c": 60},
            targets=["side"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_b"] == pytest.approx(5, rel=0.01)
        assert result["data"]["side_c"] == pytest.approx(5 * math.sqrt(3), rel=0.01)

    @pytest.mark.parametrize("task_type, params, expected_error", [
        ("SSS", {"a": 1, "b": 2, "c": 10}, "нерівність"),
        ("SAS", {"a": 3, "b": 4, "angle_c": 180}, "некоректн"),
        ("ASA", {"a": 5, "angle_b": 100, "angle_c": 90}, "сума кутів"),
    ])
    def test_invalid_input_fails_validation(self, task_type, params, expected_error):
        solver = ArbitraryTriangleSolver(
            task_type=task_type,
            params=params,
            targets=["area"],
        )
        result = solver.calculate()

        assert result["success"] is False
        assert expected_error in result["error"].lower()
