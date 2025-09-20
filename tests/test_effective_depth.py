"""Tests for effective depth calculations."""

import pytest

from soilpy.effective_depth import calc_effective_depth
from soilpy.models.foundation import Foundation
from soilpy.models.soil_profile import SoilLayer, SoilProfile


def create_soil_profile() -> SoilProfile:
    """Create a test soil profile."""
    return SoilProfile(
        ground_water_level=5.0,
        layers=[
            SoilLayer(
                thickness=3.0,
                dry_unit_weight=1.8,
                saturated_unit_weight=1.9,
                depth=3.0,
            ),
            SoilLayer(
                thickness=5.0,
                dry_unit_weight=1.9,
                saturated_unit_weight=2.0,
                depth=8.0,
            ),
            SoilLayer(
                thickness=50.0,
                dry_unit_weight=2.0,
                saturated_unit_weight=2.1,
                depth=58.0,
            ),
        ],
    )


def create_foundation_data() -> Foundation:
    """Create test foundation data."""
    return Foundation(
        foundation_width=10.0,
        foundation_length=20.0,
        foundation_depth=2.0,
    )


class TestEffectiveDepth:
    """Test cases for effective depth calculations."""

    def test_effective_depth(self):
        """Test effective depth calculation."""
        soil_profile = create_soil_profile()
        foundation_data = create_foundation_data()
        foundation_pressure = 50.0

        effective_depth = calc_effective_depth(soil_profile, foundation_data, foundation_pressure)
        expected_depth = 34.41
        assert abs(effective_depth - expected_depth) < 1e-2
