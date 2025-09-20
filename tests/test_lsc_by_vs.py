"""Tests for local soil classification by VS calculations."""

import pytest

from soilpy.enums import SelectionMethod
from soilpy.local_soil_class.by_vs import calc_lsc_by_vs
from soilpy.models.masw import Masw, MaswExp, MaswLayer


class TestLscByVs:
    """Test cases for local soil classification by VS calculations."""

    def create_layer(self, thickness: float, vs: float) -> MaswLayer:
        """Create a MASW layer with specified thickness and VS value."""
        return MaswLayer(
            thickness=thickness,
            vs=vs,
            vp=0.0,
            depth=None,
        )

    def test_case_1(self):
        """Case 1: All vs > 0 & depth < 30."""
        exp = MaswExp(
            name="Test exp",
            layers=[
                self.create_layer(5.0, 1000.0),
                self.create_layer(10.0, 1500.0),
            ],  # total depth = 15
        )

        masw = Masw(
            exps=[exp],
            idealization_method=SelectionMethod.MIN,
        )

        result = calc_lsc_by_vs(masw)
        assert len(result.layers) == 2
        assert abs(result.vs_30 - 1285.71) < 1e-2  # harmonic average
        assert result.soil_class == "ZB"  # low vs_30 leads to ZB

    def test_case_2(self):
        """Case 2: One vs = 0 & depth = 30."""
        exp = MaswExp(
            name="Test Exp",
            layers=[
                self.create_layer(10.0, 1500.0),
                self.create_layer(10.0, 0.0),  # should be skipped
                self.create_layer(10.0, 3000.0),
            ],
        )

        masw = Masw(
            exps=[exp],
            idealization_method=SelectionMethod.MIN,
        )

        result = calc_lsc_by_vs(masw)

        assert len(result.layers) == 2
        assert result.vs_30 == 3000.0
        assert result.soil_class == "ZA"  # high vs_30 leads to ZA

    def test_case_3(self):
        """Case 3: All vs > 0 & depth > 30."""
        exp = MaswExp(
            name="Test Exp",
            layers=[
                self.create_layer(10.0, 1000.0),
                self.create_layer(10.0, 2000.0),
                self.create_layer(20.0, 4000.0),  # only 10 m of this will be used
            ],
        )

        masw = Masw(
            exps=[exp],
            idealization_method=SelectionMethod.MIN,
        )

        result = calc_lsc_by_vs(masw)

        assert len(result.layers) == 3
        assert abs(result.vs_30 - 1714.28) < 1e-2  # harmonic average
        assert result.soil_class == "ZA"
