import pytest

from core.polygons.quadrangles.trapezoid import TrapezoidSolver


class TestTrapezoidSolver:
    def test_bases_and_height_finds_area(self):
        solver = TrapezoidSolver(
            task_type="TRAPEZOID_ABH",
            params={"a": 10, "b": 6, "h": 4},
            targets=["midline", "area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["midline"] == pytest.approx(8)
        assert result["data"]["area"] == pytest.approx(32)

    def test_midline_and_height_finds_area(self):
        solver = TrapezoidSolver(
            task_type="TRAPEZOID_MIDLINE_HEIGHT",
            params={"m": 8, "h": 4},
            targets=["area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(32)

    def test_area_and_bases_finds_height(self):
        solver = TrapezoidSolver(
            task_type="TRAPEZOID_AREA_BASES",
            params={"a": 10, "b": 6, "S": 32},
            targets=["height"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["height"] == pytest.approx(4)

    @pytest.mark.parametrize("task_type, params", [
        ("TRAPEZOID_ABH", {"a": 0, "b": 6, "h": 4}),
        ("ISOSCELES_TRAPEZOID_BASES_LEG", {"a": 10, "b": 6, "c": 1}),
    ])
    def test_invalid_input_fails_validation(self, task_type, params):
        solver = TrapezoidSolver(task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()
        assert result["success"] is False
