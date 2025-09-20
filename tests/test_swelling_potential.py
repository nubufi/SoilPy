"""Tests for swelling potential calculations."""

import pytest

from soilpy.models import Foundation, SoilLayer, SoilProfile
from soilpy.swelling_potential import calc_swelling_potential


class TestSwellingPotential:
    """Test cases for swelling potential calculations."""

    def create_soil_profile(self) -> SoilProfile:
        """Creates a reusable soil profile for testing."""
        return SoilProfile(
            ground_water_level=5.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=1.9,
                    depth=3.0,
                    liquid_limit=43.9,
                    plastic_limit=21.3,
                    water_content=23.7,
                ),
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.9,
                    saturated_unit_weight=2.0,
                    depth=8.0,
                    liquid_limit=58.85,
                    plastic_limit=37.4,
                    water_content=75.4,
                ),
                SoilLayer(
                    thickness=50.0,
                    dry_unit_weight=2.0,
                    saturated_unit_weight=2.1,
                    depth=58.0,
                    liquid_limit=2.3,
                    plastic_limit=0.0,
                    water_content=22.5,
                ),
            ],
        )

    def create_foundation_data(self) -> Foundation:
        """Creates test foundation data."""
        return Foundation(
            foundation_width=10.0,
            foundation_length=20.0,
            foundation_depth=2.0,
        )

    def test_calc_swelling_potential(self):
        """Test swelling potential calculation."""
        soil_profile = self.create_soil_profile()
        foundation_data = self.create_foundation_data()
        foundation_pressure = 50.0

        result = calc_swelling_potential(soil_profile, foundation_data, foundation_pressure)
        expected_pressure = 8.89
        assert abs(result.data[0].swelling_pressure - expected_pressure) < 0.01
