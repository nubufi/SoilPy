"""Tests for soil profile model functions."""

import pytest

from soilpy.models import SoilLayer, SoilProfile


class TestSoilProfile:
    """Test cases for soil profile model functions."""

    def setup_soil_profile(self) -> SoilProfile:
        """Creates a reusable soil profile for testing."""
        return SoilProfile(
            layers=[
                SoilLayer(
                    thickness=2.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                ),
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.6,
                    saturated_unit_weight=1.9,
                ),
            ],
            ground_water_level=2.5,  # Groundwater level at 2.5m
        )

    def test_calc_layer_depths(self):
        """Test layer depth and center calculations."""
        profile = self.setup_soil_profile()
        assert profile.layers[0].depth == 2.0
        assert profile.layers[1].depth == 5.0
        assert profile.layers[0].center == 1.0
        assert profile.layers[1].center == 3.5

    def test_get_layer_index(self):
        """Test layer index retrieval at different depths."""
        profile = self.setup_soil_profile()
        assert profile.get_layer_index(1.0) == 0
        assert profile.get_layer_index(3.0) == 1
        assert profile.get_layer_index(5.0) == 1

    def test_calc_normal_stress(self):
        """Test normal stress calculations at different depths."""
        profile = self.setup_soil_profile()

        assert abs(profile.calc_normal_stress(1.0) - 1.8) < 1e-3
        assert abs(profile.calc_normal_stress(2.0) - 3.6) < 1e-3
        assert abs(profile.calc_normal_stress(3.0) - 5.35) < 1e-3

    def test_calc_effective_stress(self):
        """Test effective stress calculations at different depths."""
        profile = self.setup_soil_profile()

        assert abs(profile.calc_effective_stress(1.0) - 1.8) < 1e-3
        assert abs(profile.calc_effective_stress(2.0) - 3.6) < 1e-3
        assert abs(profile.calc_effective_stress(3.0) - 4.8595) < 1e-3
