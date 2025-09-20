"""Tests for consolidation settlement by coefficient of volume compressibility (Mv) calculations."""

import pytest

from soilpy.consolidation_settlement.by_mv import calc_single_layer_settlement


class TestConsolidationSettlementByMv:
    """Test cases for consolidation settlement by coefficient of volume compressibility (Mv) calculations."""

    def test_settlement_by_mv(self):
        """Test single layer settlement calculation using coefficient of volume compressibility."""
        mv = 0.004
        thickness = 10.0
        delta_stress = 10.0

        expected_settlement = 40.0

        settlement = calc_single_layer_settlement(mv, thickness, delta_stress)

        assert settlement == expected_settlement
