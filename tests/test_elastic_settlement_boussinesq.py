"""Tests for elastic settlement Boussinesq calculations."""

import pytest

from soilpy.elastic_settlement.boussinesq import (
    calc_elastic_settlement,
    calc_ip,
    single_layer_settlement,
)
from soilpy.models import Foundation, SoilLayer, SoilProfile


class TestElasticSettlementBoussinesq:
    """Test cases for elastic settlement Boussinesq calculations."""

    def create_soil_profile(self) -> SoilProfile:
        """Create a test soil profile."""
        return SoilProfile(
            ground_water_level=5.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=1.9,
                    elastic_modulus=1500.0,
                    poissons_ratio=0.4,
                    depth=3.0,
                ),
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.9,
                    saturated_unit_weight=2.0,
                    elastic_modulus=6000.0,
                    poissons_ratio=0.4,
                    depth=8.0,
                ),
                SoilLayer(
                    thickness=50.0,
                    dry_unit_weight=2.0,
                    saturated_unit_weight=2.1,
                    elastic_modulus=7500.0,
                    poissons_ratio=0.4,
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
        )

    def test_calc_ip(self):
        """Test influence factor calculation."""
        h = 5.0
        b = 10.0
        l = 20.0
        u = 0.1

        result = calc_ip(h, b, l, u)
        expected = 0.222

        assert abs(result - expected) < 1e-3

    def test_calc_single_layer_settlement(self):
        """Test single layer settlement calculation."""
        h = 2.0
        u = 0.4
        e = 6000.0
        l = 20.0
        b = 10.0
        df = 6.0
        q_net = 88.3

        result = single_layer_settlement(h, u, e, l, b, df, q_net)
        expected = 1.05

        assert abs(result - expected) < 1e-3

    def test_calc_elastic_settlement(self):
        """Test elastic settlement calculation for multiple layers."""
        soil_profile = self.create_soil_profile()
        foundation_data = self.create_foundation_data()
        foundation_pressure = 50.0

        result = calc_elastic_settlement(soil_profile, foundation_data, foundation_pressure)
        expected_settlements = [1.058, 2.195, 4.613]

        for settlement, expected in zip(result.settlement_per_layer, expected_settlements):
            assert abs(settlement - expected) < 1e-3
