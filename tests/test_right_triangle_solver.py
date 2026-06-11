import pytest

from core.polygons.triangles.right_triangle import RightTriangleSolver


class TestRightTriangleSolver:
    def test_legs_given_finds_hypotenuse(self):
        solver = RightTriangleSolver(
            task_type="RIGHT_LEGS",
            params={"a": 3, "b": 4},
            targets=["side"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_c"] == pytest.approx(5)

    def test_legs_given_finds_area_and_perimeter(self):
        solver = RightTriangleSolver(
            task_type="RIGHT_LEGS",
            params={"a": 3, "b": 4},
            targets=["area", "perimeter"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["area"] == pytest.approx(6)
        assert result["data"]["perimeter"] == pytest.approx(12)

    def test_leg_and_hypotenuse_given_finds_second_leg(self):
        solver = RightTriangleSolver(
            task_type="RIGHT_LEG_HYPOTENUSE",
            params={"a": 3, "c": 5},
            targets=["side"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["side_b"] == pytest.approx(4)

    def test_legs_given_finds_inscribed_and_circumscribed_radii(self):
        solver = RightTriangleSolver(
            task_type="RIGHT_LEGS",
            params={"a": 3, "b": 4},
            targets=["incircle", "circumcircle"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["r_inscribed"] == pytest.approx(1)
        assert result["data"]["r_circumscribed"] == pytest.approx(2.5)

    @pytest.mark.parametrize("params, expected_error", [
        ({"a": 0, "b": 4}, "додатн"),
        ({"a": 5, "c": 3}, "гіпотенуз"),
    ])
    def test_invalid_input_fails_validation(self, params, expected_error):
        task_type = "RIGHT_LEG_HYPOTENUSE" if "c" in params else "RIGHT_LEGS"
        solver = RightTriangleSolver(
            task_type=task_type,
            params=params,
            targets=["area"],
        )
        result = solver.calculate()

        assert result["success"] is False
        assert expected_error in result["error"].lower()
