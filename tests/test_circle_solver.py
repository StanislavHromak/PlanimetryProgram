import math

import pytest

from core.curves.circle import CircleSolver


class TestCircleSolver:
    def test_radius_given_finds_all_targets(self):
        solver = CircleSolver(
            task_type="CIRCLE_RADIUS",
            params={"radius": 5},
            targets=["diameter", "circumference", "area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["diameter"] == pytest.approx(10)
        assert result["data"]["circumference"] == pytest.approx(2 * math.pi * 5, rel=0.01)
        assert result["data"]["area"] == pytest.approx(math.pi * 25, rel=0.01)
        assert result["image"] is not None

    def test_diameter_given_finds_radius_and_area(self):
        solver = CircleSolver(
            task_type="CIRCLE_DIAMETER",
            params={"diameter": 10},
            targets=["radius", "area"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["radius"] == pytest.approx(5)
        assert result["data"]["area"] == pytest.approx(math.pi * 25, rel=0.01)

    def test_area_given_finds_radius(self):
        solver = CircleSolver(
            task_type="CIRCLE_AREA",
            params={"area": math.pi},
            targets=["radius"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["radius"] == pytest.approx(1)

    def test_circumference_given_finds_radius(self):
        solver = CircleSolver(
            task_type="CIRCLE_CIRCUMFERENCE",
            params={"circumference": 2 * math.pi},
            targets=["radius"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["radius"] == pytest.approx(1)

    @pytest.mark.parametrize("task_type, params", [
        ("CIRCLE_RADIUS", {"radius": 0}),
        ("CIRCLE_RADIUS", {"radius": -3}),
        ("CIRCLE_DIAMETER", {"diameter": -1}),
    ])
    def test_non_positive_input_fails_validation(self, task_type, params):
        solver = CircleSolver(task_type=task_type, params=params, targets=["area"])
        result = solver.calculate()

        assert result["success"] is False
        assert "додатн" in result["error"].lower()
