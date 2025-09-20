"""Tests for Tezcan-Ozdemir bearing capacity calculations."""

import pytest

from soilpy.bearing_capacity.tezcan_ozdemir import calc_bearing_capacity
from soilpy.enums import SelectionMethod
from soilpy.models.foundation import Foundation
from soilpy.models.masw import Masw, MaswExp, MaswLayer
from soilpy.models.soil_profile import SoilLayer, SoilProfile


def create_soil_profile() -> SoilProfile:
    """Create a test soil profile."""
    return SoilProfile(
        ground_water_level=0.0,
        layers=[
            SoilLayer(
                thickness=5.0,
                dry_unit_weight=1.8,
                saturated_unit_weight=2.0,
                depth=5.0,
            )
        ],
    )


def create_masw_exp(vs: float) -> Masw:
    """Create a test MASW experiment."""
    return Masw(
        exps=[
            MaswExp(
                layers=[
                    MaswLayer(
                        thickness=5.0,
                        depth=5.0,
                        vs=vs,
                        vp=0.0,
                    )
                ],
                name="Test",
            )
        ],
        idealization_method=SelectionMethod.MIN,
    )


class TestTezcanOzdemir:
    """Test cases for Tezcan-Ozdemir bearing capacity calculations."""

    def test_bc_tezcan_ozdemir_1(self):
        """Test for VS >= 4000"""
        soil_profile = create_soil_profile()
        masw_exp = create_masw_exp(4001.0)
        foundation = Foundation(
            foundation_depth=5.0,
            foundation_width=1.0,
            foundation_length=1.0,
        )

        foundation_pressure = 100.0

        result = calc_bearing_capacity(soil_profile, masw_exp, foundation, foundation_pressure)

        assert result.is_safe
        assert abs(result.allowable_bearing_capacity - 568.142) < 1e-5
        assert abs(result.safety_factor - 1.4) < 1e-5

    def test_bc_tezcan_ozdemir_2(self):
        """Test for VS = 3000"""
        soil_profile = create_soil_profile()
        masw_exp = create_masw_exp(3000.0)
        foundation = Foundation(
            foundation_depth=5.0,
            foundation_width=1.0,
            foundation_length=1.0,
        )

        foundation_pressure = 100.0

        result = calc_bearing_capacity(soil_profile, masw_exp, foundation, foundation_pressure)

        assert result.is_safe
        assert abs(result.allowable_bearing_capacity - 272.72727) < 1e-5
        assert abs(result.safety_factor - 2.2) < 1e-5

    def test_bc_tezcan_ozdemir_3(self):
        """Test for VS = 400"""
        soil_profile = create_soil_profile()
        masw_exp = create_masw_exp(400.0)
        foundation = Foundation(
            foundation_depth=5.0,
            foundation_width=1.0,
            foundation_length=1.0,
        )

        foundation_pressure = 100.0

        result = calc_bearing_capacity(soil_profile, masw_exp, foundation, foundation_pressure)

        assert not result.is_safe
        assert abs(result.allowable_bearing_capacity - 20.0) < 1e-5
        assert abs(result.safety_factor - 4.0) < 1e-5
