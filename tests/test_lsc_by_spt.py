"""Tests for local soil classification by SPT calculations."""

import pytest

from soilpy.enums import SelectionMethod
from soilpy.local_soil_class.by_spt import calc_lsc_by_spt
from soilpy.models.spt import SPT, NValue, SPTBlow, SPTExp


class TestLscBySpt:
    """Test cases for local soil classification by SPT calculations."""

    def create_blow(self, depth: float, n: int) -> SPTBlow:
        """Create an SPT blow with specified depth and N value."""
        return SPTBlow(
            depth=depth,
            n=NValue(value="R") if n == 50 else NValue.from_i32(n),
        )

    def test_case_1(self):
        """Case 1: All spt > 0 & no refusal & depth < 30."""
        exp = SPTExp(
            name="Test exp",
            blows=[
                self.create_blow(5.0, 10),
                self.create_blow(10.0, 15),
                self.create_blow(15.0, 20),
            ],  # total depth = 15
        )
        spt = SPT(
            energy_correction_factor=1.0,
            diameter_correction_factor=1.0,
            sampler_correction_factor=1.0,
            idealization_method=SelectionMethod.MIN,
            exps=[exp],
        )

        result = calc_lsc_by_spt(spt)
        assert len(result.layers) == 3
        assert abs(result.n_30 - 13.84) < 1e-2  # harmonic average
        assert result.soil_class == "ZE"

    def test_case_2(self):
        """Case 2: One spt = R & depth = 30."""
        exp = SPTExp(
            name="Test Exp",
            blows=[
                self.create_blow(10.0, 15),
                self.create_blow(20.0, 50),  # Refusal
                self.create_blow(30.0, 30),
            ],
        )
        spt = SPT(
            energy_correction_factor=1.0,
            diameter_correction_factor=1.0,
            sampler_correction_factor=1.0,
            idealization_method=SelectionMethod.MIN,
            exps=[exp],
        )

        result = calc_lsc_by_spt(spt)

        assert len(result.layers) == 3
        assert result.n_30 == 25.0
        assert result.soil_class == "ZD"  # n_30 = 25 leads to ZD

    def test_case_3(self):
        """Case 3: All spt > 0 & no refusal & depth > 30."""
        exp = SPTExp(
            name="Test Exp",
            blows=[
                self.create_blow(10.0, 10),
                self.create_blow(20.0, 20),
                self.create_blow(40.0, 40),  # only 10 m of this will be used
            ],
        )
        spt = SPT(
            energy_correction_factor=1.0,
            diameter_correction_factor=1.0,
            sampler_correction_factor=1.0,
            idealization_method=SelectionMethod.MIN,
            exps=[exp],
        )

        result = calc_lsc_by_spt(spt)

        assert len(result.layers) == 3
        assert abs(result.n_30 - 17.14) < 1e-2  # harmonic average
        assert result.soil_class == "ZD"
