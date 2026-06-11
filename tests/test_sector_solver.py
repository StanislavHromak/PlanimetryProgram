import math

import pytest

from core.curves.sector import SectorSolver


class TestSectorSolver:
    def test_radius_and_angle_finds_targets(self):
        solver = SectorSolver(
            task_type="SECTOR_AND_ARC",
            params={"radius": 10, "angle": 90},
            targets=["arc_length", "sector_area", "chord_length"],
        )
        result = solver.calculate()

        assert result["success"] is True
        assert result["data"]["arc_length"] == pytest.approx(math.pi * 5, rel=0.01)
        assert result["data"]["sector_area"] == pytest.approx(25 * math.pi, rel=0.01)
        assert result["data"]["chord_length"] == pytest.approx(10 * math.sqrt(2), rel=0.01)

    @pytest.mark.parametrize("params", [
        {"radius": 0, "angle": 90},
        {"radius": 5, "angle": 0},
        {"radius": 5, "angle": 360},
    ])
    def test_invalid_input_fails_validation(self, params):
        solver = SectorSolver(
            task_type="SECTOR_AND_ARC",
            params=params,
            targets=["arc_length"],
        )
        result = solver.calculate()
        assert result["success"] is False
