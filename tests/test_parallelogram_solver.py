import pytest

from core.polygons.quadrangles.parallelogram import ParallelogramSolver


class TestParallelogramSolver:
    def test_sides_and_angle_finds_area_and_perimeter(self):
        solver = ParallelogramSolver(
            task_type="PARALLELOGRAM_S_A",
            params={"a": 5, "b": 4, "angle": 90},
            targets=["area", "perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(20)
        assert result["data"]["perimeter"] == pytest.approx(18)

    def test_diagonals_and_angle_finds_sides(self):
        solver = ParallelogramSolver(
            task_type="PARALLELOGRAM_D_A",
            params={"d1": 6, "d2": 8, "angle": 90},
            targets=["sides"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_a"] == pytest.approx(5, rel=0.01)
        assert result["data"]["side_b"] == pytest.approx(5, rel=0.01)

    @pytest.mark.parametrize("task_type, params", [
        ("PARALLELOGRAM_S_A", {"a": 0, "b": 4, "angle": 90}),
        ("PARALLELOGRAM_S_A", {"a": 5, "b": 4, "angle": 180}),
        ("PARALLELOGRAM_D_A", {"d1": -1, "d2": 8, "angle": 90}),
    ])
    def test_invalid_input_fails_validation(self, task_type, params):
        solver = ParallelogramSolver(task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()
        assert result["success"] is False
