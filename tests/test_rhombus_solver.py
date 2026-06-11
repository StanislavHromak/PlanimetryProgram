import pytest

from core.polygons.quadrangles.rhombus import RhombusSolver


class TestRhombusSolver:
    def test_diagonals_given_finds_side_and_area(self):
        solver = RhombusSolver(
            task_type="RHOMBUS_DIAGONALS",
            params={"d1": 6, "d2": 8},
            targets=["side_a", "area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_a"] == pytest.approx(5)
        assert result["data"]["area"] == pytest.approx(24)

    def test_side_and_angle_finds_area(self):
        solver = RhombusSolver(
            task_type="RHOMBUS_SIDE_ANGLE",
            params={"a": 5, "angle": 90},
            targets=["area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(25)

    @pytest.mark.parametrize("task_type, params", [
        ("RHOMBUS_DIAGONALS", {"d1": 0, "d2": 8}),
        ("RHOMBUS_AREA_SIDE", {"a": 5, "S": 30}),
        ("RHOMBUS_DIAGONAL_SIDE", {"a": 5, "d1": 12}),
    ])
    def test_invalid_input_fails_validation(self, task_type, params):
        solver = RhombusSolver(task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()
        assert result["success"] is False
