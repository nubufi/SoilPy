"""Tests for horizontal sliding calculations."""

import pytest

from soilpy.horizontal_sliding import calc_horizontal_sliding
from soilpy.models import Foundation, Loads, SoilLayer, SoilProfile


class TestHorizontalSliding:
    """Test cases for horizontal sliding calculations."""

    def create_soil_profile(self) -> SoilProfile:
        """Create a test soil profile."""
        return SoilProfile(
            ground_water_level=5.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=1.9,
                    c_prime=1.0,
                    phi_prime=21.0,
                    phi_u=0.0,
                    cu=3.0,
                    depth=3.0,
                ),
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.9,
                    saturated_unit_weight=2.0,
                    c_prime=0.5,
                    phi_prime=28.0,
                    phi_u=20.0,
                    cu=0.0,
                    depth=8.0,
                ),
                SoilLayer(
                    thickness=50.0,
                    dry_unit_weight=2.0,
                    saturated_unit_weight=2.1,
                    c_prime=1.0,
                    phi_prime=24.0,
                    phi_u=0.0,
                    cu=5.0,
                    depth=58.0,
                ),
            ],
        )

    def create_foundation_data(self) -> Foundation:
        """Create test foundation data."""
        return Foundation(
            foundation_width=10.0,
            foundation_length=20.0,
            foundation_depth=2.0,
            surface_friction_coefficient=0.6,
        )

    def create_load_data(self) -> Loads:
        """Create test load data."""
        return Loads(
            horizontal_load_x=10.0,
            horizontal_load_y=20.0,
        )

    def test_horizontal_sliding(self):
        """Test horizontal sliding calculation."""
        soil_profile = self.create_soil_profile()
        foundation_data = self.create_foundation_data()
        load_data = self.create_load_data()
        foundation_pressure = 50.0

        result = calc_horizontal_sliding(
            soil_profile,
            foundation_data,
            load_data,
            foundation_pressure,
        )

        assert abs(result.rth - 5454.55) < 1e-2
        assert abs(result.rpk_x - 76.21) < 1e-2
        assert abs(result.rpk_y - 152.43) < 1e-2
        assert abs(result.rpt_x - 54.44) < 1e-2
        assert abs(result.rpt_y - 108.88) < 1e-2
        assert abs(result.sum_x - 5470.88) < 1e-2
        assert abs(result.sum_y - 5487.21) < 1e-2
