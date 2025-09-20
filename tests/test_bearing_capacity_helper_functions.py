"""Tests for bearing capacity helper functions."""

import pytest

from soilpy.bearing_capacity.helper_functions import (
    calc_effective_surcharge,
    calc_effective_unit_weight,
    compute_equivalent_unit_weights,
    get_soil_params,
)
from soilpy.enums import AnalysisTerm
from soilpy.models.foundation import Foundation
from soilpy.models.soil_profile import SoilLayer, SoilProfile


class TestComputeEquivalentUnitWeights:
    """Test cases for compute_equivalent_unit_weights function."""

    def test_compute_equivalent_unit_weights_1(self):
        """Test for single layer"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                )
            ],
        )
        gamma_1, gamma_2 = compute_equivalent_unit_weights(profile, 5.0)
        assert abs(gamma_1 - 1.8) < 1e-3
        assert abs(gamma_2 - 2.0) < 1e-3

    def test_compute_equivalent_unit_weights_2(self):
        """Test for 2 layers"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.7,
                    saturated_unit_weight=1.9,
                    depth=3.0,
                ),
                SoilLayer(
                    thickness=2.0,
                    dry_unit_weight=1.9,
                    saturated_unit_weight=2.1,
                    depth=5.0,
                ),
            ],
        )
        gamma_1, gamma_2 = compute_equivalent_unit_weights(profile, 5.0)
        assert abs(gamma_1 - 1.78) < 1e-3
        assert abs(gamma_2 - 1.98) < 1e-3

    def test_compute_equivalent_unit_weights_3(self):
        """Test for 3 layers"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=2.0,
                    dry_unit_weight=1.6,
                    saturated_unit_weight=1.8,
                    depth=2.0,
                ),
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                ),
                SoilLayer(
                    thickness=4.0,
                    dry_unit_weight=2.0,
                    saturated_unit_weight=2.2,
                    depth=9.0,
                ),
            ],
        )
        gamma_1, gamma_2 = compute_equivalent_unit_weights(profile, 7.0)
        assert abs(gamma_1 - 1.8) < 1e-3
        assert abs(gamma_2 - 2.0) < 1e-3

    def test_compute_equivalent_unit_weights_4(self):
        """Test for depth limit at layer boundary"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.7,
                    saturated_unit_weight=1.9,
                    depth=3.0,
                ),
                SoilLayer(
                    thickness=2.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                ),
            ],
        )
        gamma_1, gamma_2 = compute_equivalent_unit_weights(profile, 3.0)
        assert abs(gamma_1 - 1.7) < 1e-3
        assert abs(gamma_2 - 1.9) < 1e-3

    def test_compute_equivalent_unit_weights_5(self):
        """Test for depth limit inside layer"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.7,
                    saturated_unit_weight=1.9,
                    depth=3.0,
                ),
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=6.0,
                ),
            ],
        )
        gamma_1, gamma_2 = compute_equivalent_unit_weights(profile, 4.0)
        assert abs(gamma_1 - 1.725) < 1e-3
        assert abs(gamma_2 - 1.925) < 1e-3

    def test_compute_equivalent_unit_weights_6(self):
        """Test for depth limit outside profile"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.7,
                    saturated_unit_weight=1.9,
                    depth=3.0,
                ),
                SoilLayer(
                    thickness=3.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=6.0,
                ),
            ],
        )
        gamma_1, gamma_2 = compute_equivalent_unit_weights(profile, 10.0)
        assert abs(gamma_1 - 1.75) < 1e-3
        assert abs(gamma_2 - 1.95) < 1e-3


class TestCalcEffectiveSurcharge:
    """Test cases for calc_effective_surcharge function."""

    def test_calc_effective_surcharge_1(self):
        """Case 1: Foundation above groundwater (gwt > Df + B)"""
        profile = SoilProfile(
            ground_water_level=10.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                )
            ],
        )
        building = Foundation(
            foundation_depth=3.0,
            effective_width=2.0,
        )
        pressure = calc_effective_surcharge(profile, building, AnalysisTerm.SHORT)
        assert abs(pressure - 5.4) < 1e-3, f"Expected 5.4, got {pressure}"

    def test_calc_effective_surcharge_2(self):
        """Case 2: Foundation below groundwater (0 < gwt <= Df)"""
        profile = SoilProfile(
            ground_water_level=2.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                )
            ],
        )
        building = Foundation(
            foundation_depth=5.0,
            effective_width=2.0,
        )
        pressure = calc_effective_surcharge(profile, building, AnalysisTerm.SHORT)
        assert abs(pressure - 6.657) < 1e-3, f"Expected 6.657, got {pressure}"

    def test_calc_effective_surcharge_3(self):
        """Case 3: Groundwater at surface (gwt = 0) with short term"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                )
            ],
        )
        building = Foundation(
            foundation_depth=7.0,
            effective_width=3.0,
        )
        pressure = calc_effective_surcharge(profile, building, AnalysisTerm.SHORT)
        assert abs(pressure - 7.133) < 1e-3, f"Expected 7.133, got {pressure}"

    def test_calc_effective_surcharge_4(self):
        """Case 4: Groundwater at surface (gwt = 0) with long term"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                )
            ],
        )
        building = Foundation(
            foundation_depth=7.0,
            effective_width=3.0,
        )
        pressure = calc_effective_surcharge(profile, building, AnalysisTerm.LONG)
        assert abs(pressure - 12.6) < 1e-3, f"Expected 12.6, got {pressure}"


class TestCalcEffectiveUnitWeight:
    """Test cases for calc_effective_unit_weight function."""

    def test_calc_effective_unit_weight_1(self):
        """Case 1: Entire foundation is below groundwater level (gwt <= Df)"""
        profile = SoilProfile(
            ground_water_level=2.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                    depth=5.0,
                )
            ],
        )

        foundation = Foundation(
            foundation_depth=5.0,
            effective_width=2.0,
        )

        gamma = calc_effective_unit_weight(profile, foundation, AnalysisTerm.SHORT)
        assert abs(gamma - 1.019) < 1e-3, f"Expected 1.019, got {gamma}"

    def test_calc_effective_unit_weight_2(self):
        """Case 2: Groundwater is between Df and Df + B (partially submerged zone)"""
        profile = SoilProfile(
            ground_water_level=6.0,
            layers=[
                SoilLayer(
                    thickness=4.0,
                    dry_unit_weight=1.7,
                    saturated_unit_weight=2.1,
                    depth=4.0,
                )
            ],
        )

        foundation = Foundation(
            foundation_depth=5.0,
            effective_width=2.0,
        )

        gamma = calc_effective_unit_weight(profile, foundation, AnalysisTerm.SHORT)
        assert abs(gamma - 1.409) < 1e-3, f"Expected 1.409, got {gamma}"

    def test_calc_effective_unit_weight_3(self):
        """Case 3: Foundation and entire zone above groundwater (gwt > Df + B)"""
        profile = SoilProfile(
            ground_water_level=10.0,
            layers=[
                SoilLayer(
                    thickness=4.0,
                    dry_unit_weight=1.9,
                    saturated_unit_weight=2.3,
                    depth=4.0,
                )
            ],
        )

        foundation = Foundation(
            foundation_depth=6.0,
            effective_width=2.0,
        )

        gamma = calc_effective_unit_weight(profile, foundation, AnalysisTerm.SHORT)
        assert abs(gamma - 1.9) < 1e-3, f"Expected 1.9, got {gamma}"

    def test_calc_effective_unit_weight_4(self):
        """Case 4: Short-term vs. Long-term — long-term makes gwt = Df + B"""
        profile = SoilProfile(
            ground_water_level=3.0,
            layers=[
                SoilLayer(
                    thickness=4.0,
                    dry_unit_weight=1.7,
                    saturated_unit_weight=2.1,
                    depth=4.0,
                )
            ],
        )

        foundation = Foundation(
            foundation_depth=6.0,
            effective_width=2.0,
        )

        gamma = calc_effective_unit_weight(profile, foundation, AnalysisTerm.LONG)
        assert abs(gamma - 1.7) < 1e-3, f"Expected 1.7, got {gamma}"


class TestGetSoilParams:
    """Test cases for get_soil_params function."""

    def test_get_soil_params_1(self):
        """Case 1: Short-term loading — returns undrained cohesion and undrained friction angle"""
        profile = SoilProfile(
            ground_water_level=2.0,
            layers=[
                SoilLayer(
                    thickness=5.0,
                    depth=5.0,
                    cu=25.0,
                    phi_u=20.0,
                    c_prime=5.0,
                    phi_prime=30.0,
                    dry_unit_weight=1.8,
                    saturated_unit_weight=2.0,
                )
            ],
        )

        foundation = Foundation(
            foundation_depth=3.0,
            effective_width=2.0,
        )

        params = get_soil_params(profile, foundation, AnalysisTerm.SHORT)

        assert params.friction_angle == 20.0
        assert params.cohesion == 25.0
        assert abs(params.unit_weight - 1.019) < 1e-3, f"Expected 1.019, got {params.unit_weight}"

    def test_get_soil_params_2(self):
        """Case 2: Long-term loading — returns effective parameters"""
        profile = SoilProfile(
            ground_water_level=0.0,
            layers=[
                SoilLayer(
                    thickness=4.0,
                    depth=4.0,
                    cu=18.0,
                    phi_u=25.0,
                    c_prime=8.0,
                    phi_prime=32.0,
                    dry_unit_weight=1.9,
                    saturated_unit_weight=2.1,
                )
            ],
        )

        foundation = Foundation(
            foundation_depth=3.5,
            effective_width=2.0,
        )

        params = get_soil_params(profile, foundation, AnalysisTerm.LONG)

        assert params.friction_angle == 32.0
        assert params.cohesion == 8.0
        assert abs(params.unit_weight - 1.9) < 1e-3, f"Expected 1.9, got {params.unit_weight}"
