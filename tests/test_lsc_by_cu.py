"""Tests for local soil classification by CU calculations."""

import pytest

from soilpy.local_soil_class.by_cu import calc_lsc_by_cu
from soilpy.models.soil_profile import SoilLayer, SoilProfile


class TestLscByCu:
    """Test cases for local soil classification by CU calculations."""

    def create_layer(self, thickness: float, cu: float) -> SoilLayer:
        """Create a soil layer with specified thickness and CU value."""
        return SoilLayer(
            thickness=thickness,
            cu=cu,
        )

    def test_case_1(self):
        """Case 1: All cu > 0 & depth < 30."""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                self.create_layer(5.0, 10.0),
                self.create_layer(10.0, 15.0),
            ],  # total depth = 15
        )

        result = calc_lsc_by_cu(profile)
        assert len(result.layers) == 2
        assert abs(result.cu_30 - 12.86) < 1e-2  # harmonic average
        assert result.soil_class == "ZD"  # low cu_30 leads to ZD

    def test_case_2(self):
        """Case 2: One cu = 0 & depth = 30."""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                self.create_layer(10.0, 15.0),
                self.create_layer(10.0, 0.0),  # should be skipped
                self.create_layer(10.0, 30.0),
            ],
        )

        result = calc_lsc_by_cu(profile)

        assert len(result.layers) == 2
        assert result.cu_30 == 30.0
        assert result.soil_class == "ZC"  # high cu_30 leads to ZC

    def test_case_3(self):
        """Case 3: All cu > 0 & depth > 30."""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                self.create_layer(10.0, 10.0),
                self.create_layer(10.0, 20.0),
                self.create_layer(20.0, 40.0),  # only 10 m of this will be used
            ],
        )

        result = calc_lsc_by_cu(profile)

        assert len(result.layers) == 3
        assert abs(result.cu_30 - 17.14) < 1e-2  # harmonic average
        assert result.soil_class == "ZD"
