"""Tests for liquefaction VS Andrus-Stokoe calculations."""

import pytest

from soilpy.liquefaction.vs.andrus_stokoe import calc_crr75, calc_settlement, calc_vs1c


class TestLiquefactionVsAndrusStokoe:
    """Test cases for liquefaction VS Andrus-Stokoe calculations."""

    def test_calc_vs1c_low_fine_content(self):
        """Test Vs1c calculation for low fine content (fc <= 5.0)."""
        fine_content = 3.0
        expected = 215.0
        result = calc_vs1c(fine_content)
        assert abs(result - expected) < 1e-6

    def test_calc_vs1c_mid_fine_content(self):
        """Test Vs1c calculation for mid fine content (5.0 < fc <= 35.0)."""
        fine_content = 20.0
        expected = 215.0 - 0.5 * (fine_content - 5.0)  # = 207.5
        result = calc_vs1c(fine_content)
        assert abs(result - expected) < 1e-6

    def test_calc_vs1c_high_fine_content(self):
        """Test Vs1c calculation for high fine content (fc > 35.0)."""
        fine_content = 40.0
        expected = 200.0
        result = calc_vs1c(fine_content)
        assert abs(result - expected) < 1e-6

    def test_calc_crr75_single_case(self):
        """Test CRR calculation for a single case."""
        vs1 = 180.0  # m/s
        vs1c = 200.0  # m/s
        effective_stress = 7.0  # ton/m²
        expected = 0.708

        result = calc_crr75(vs1, vs1c, effective_stress)
        assert abs(result - expected) < 1e-2

    def test_calc_settlement(self):
        """Test settlement calculation due to liquefaction."""
        fs = 1.0
        layer_thickness = 1.0  # m
        vs1 = 180.0  # Corrected N60 value

        expected = 1.03
        result = calc_settlement(fs, layer_thickness, vs1)

        assert abs(result - expected) < 1e-2
