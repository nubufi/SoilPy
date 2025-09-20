"""Tests for consolidation settlement by compression index calculations."""

import pytest

from soilpy.consolidation_settlement.by_compression_index import (
    calc_single_layer_settlement,
)


class TestConsolidationSettlementByCompressionIndex:
    """Test cases for consolidation settlement by compression index calculations."""

    def test_calc_single_layer_settlement(self):
        """Test single layer settlement calculation using compression index method."""
        # Test case 1: Normal case
        h = 10.0  # Thickness of the layer [m]
        cc = 0.2  # Compression Index (Cc)
        cr = 0.2  # Recompression Index (Cr)
        e0 = 0.3  # Initial Void Ratio (e₀)
        gp = 10.0  # Preconsolidation Pressure [t]
        g0 = 20.0  # Initial Effective Stress [t]
        delta_stress = 10.0  # Stress increase due to foundation [t]

        expected = 27.091  # Expected settlement [cm]
        settlement = calc_single_layer_settlement(h, cc, cr, e0, gp, g0, delta_stress)
        assert abs(settlement - expected) < 0.001
