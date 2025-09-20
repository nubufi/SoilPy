"""Tests for liquefaction SPT Seed-Idriss calculations."""

import pytest

from soilpy.liquefaction.spt.seed_idriss import calc_crr75, calc_settlement


class TestLiquefactionSptSeedIdriss:
    """Test cases for liquefaction SPT Seed-Idriss calculations."""

    def test_calc_crr75(self):
        """Test cyclic resistance ratio (CRR) calculation."""
        n1_60_f = 15
        effective_stress = 8.0  # ton/m²

        expected = 1.28

        result = calc_crr75(n1_60_f, effective_stress)
        assert abs(result - expected) < 1e-2

    def test_calc_settlement(self):
        """Test settlement calculation due to liquefaction."""
        fs = 1.0
        layer_thickness = 1.0  # m
        n60 = 11  # Corrected N60 value

        expected = 1.7
        result = calc_settlement(fs, layer_thickness, n60)

        assert abs(result - expected) < 1e-1
