"""Tests for soil coefficient calculations."""

import pytest

from soilpy.soil_coefficient import calc_by_bearing_capacity, calc_by_settlement


class TestSoilCoefficient:
    """Test cases for soil coefficient calculations."""

    def test_calc_soil_coefficient_by_settlement_positive(self):
        """Test soil coefficient calculation by settlement with positive settlement."""
        settlement = 2.0  # in meters
        foundation_load = 1000.0
        result = calc_by_settlement(settlement, foundation_load)
        assert abs(result - 50_000.0) < 1e-6

    def test_calc_soil_coefficient_by_settlement_zero(self):
        """Test soil coefficient calculation by settlement with zero settlement."""
        settlement = 0.0  # in meters
        foundation_load = 1000.0
        result = calc_by_settlement(settlement, foundation_load)
        assert result == 999_999.0

    def test_calc_soil_coefficient_by_bearing_capacity(self):
        """Test soil coefficient calculation by bearing capacity."""
        bearing_capacity = 250.0
        result = calc_by_bearing_capacity(bearing_capacity)
        assert abs(result - 100_000.0) < 1e-6
