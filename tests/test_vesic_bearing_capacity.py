"""Tests for Vesic bearing capacity calculations."""

import pytest

from soilpy.bearing_capacity.model import BearingCapacityFactors
from soilpy.bearing_capacity.vesic import (
    calc_base_factors,
    calc_bearing_capacity_factors,
    calc_depth_factors,
    calc_ground_factors,
    calc_inclination_factors,
    calc_shape_factors,
)
from soilpy.models.foundation import Foundation
from soilpy.models.loads import Loads


class TestCalcBearingCapacityFactors:
    """Test cases for calc_bearing_capacity_factors function."""

    def test_calc_bearing_capacity_factors_1(self):
        """Case 1: φ = 0°, pure cohesive soil — should return Nc = 5.14, Nq = 1.0, Ng = 0.0"""
        phi = 0.0
        result = calc_bearing_capacity_factors(phi)

        assert abs(result.nc - 5.14) < 1e-3
        assert abs(result.nq - 1.0) < 1e-3
        assert abs(result.ng - 0.0) < 1e-3

    def test_calc_bearing_capacity_factors_2(self):
        """Case 2: φ = 10° — soft granular soil"""
        phi = 10.0
        result = calc_bearing_capacity_factors(phi)

        assert abs(result.nc - 8.345) < 1e-3
        assert abs(result.nq - 2.471) < 1e-3
        assert abs(result.ng - 0.519) < 1e-3

    def test_calc_bearing_capacity_factors_3(self):
        """Case 3: φ = 30° — typical for dense sand"""
        phi = 30.0
        result = calc_bearing_capacity_factors(phi)

        assert abs(result.nc - 30.14) < 1e-3
        assert abs(result.nq - 18.401) < 1e-3
        assert abs(result.ng - 20.093) < 1e-3


class TestCalcShapeFactors:
    """Test cases for calc_shape_factors function."""

    def test_calc_shape_factors_1(self):
        """Case 1: φ = 0°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
            foundation_length=1.5,
        )
        phi = 0.0

        bc_factors = BearingCapacityFactors(
            nc=5.14,
            nq=1.0,
            ng=0.0,
        )

        result = calc_shape_factors(foundation, bc_factors, phi)
        assert abs(result.sc - 0.133) < 1e-3
        assert abs(result.sq - 1.0) < 1e-3
        assert abs(result.sg - 0.733) < 1e-3

    def test_calc_shape_factors_2(self):
        """Case 2: φ = 30°, B/L = 1/1.5 = 0.667, Nq = 18.401, Nc = 30.140"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
            foundation_length=1.5,
        )
        phi = 30.0

        bc_factors = BearingCapacityFactors(
            nc=30.140,
            nq=18.401,
            ng=20.093,
        )

        result = calc_shape_factors(foundation, bc_factors, phi)
        assert abs(result.sc - 1.407) < 1e-3
        assert abs(result.sq - 1.333) < 1e-3
        assert abs(result.sg - 0.733) < 1e-3


class TestCalcInclinationFactors:
    """Test cases for calc_inclination_factors function."""

    def test_calc_inclination_factors_1(self):
        """Case 1: φ = 0°, c = 10, HL = 0, HB = 0, V = 200"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=4.0,
            foundation_length=6.0,
            effective_width=1.0,
            effective_length=1.5,
        )

        loads = Loads(
            vertical_load=200.0,
            horizontal_load_x=0.0,
            horizontal_load_y=0.0,
        )

        bc_factors = BearingCapacityFactors(
            nc=1.0,
            nq=1.0,
            ng=1.0,
        )
        phi = 0.0
        cohesion = 10.0

        result = calc_inclination_factors(phi, cohesion, bc_factors, foundation, loads)
        assert abs(result.ic - 1.0) < 1e-3
        assert abs(result.iq - 1.0) < 1e-3
        assert abs(result.ig - 1.0) < 1e-3

    def test_calc_inclination_factors_2(self):
        """Case 2: φ = 30°, c = 0, HL = 0, HB = 0, V = 200"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
            foundation_length=1.5,
            effective_width=1.0,
            effective_length=1.5,
        )

        loads = Loads(
            vertical_load=200.0,
            horizontal_load_x=0.0,
            horizontal_load_y=0.0,
        )
        bc_factors = BearingCapacityFactors(
            nc=1.0,
            nq=18.401,
            ng=1.0,
        )
        phi = 30.0
        cohesion = 0.0

        result = calc_inclination_factors(phi, cohesion, bc_factors, foundation, loads)
        assert abs(result.ic - 1.0) < 1e-3
        assert abs(result.iq - 1.0) < 1e-3
        assert abs(result.ig - 1.0) < 1e-3

    def test_calc_inclination_factors_3(self):
        """Case 3: φ = 30°, c = 10, HL = 0, HB = 10, V = 200"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
            foundation_length=1.5,
            effective_width=1.0,
            effective_length=1.5,
        )

        loads = Loads(
            vertical_load=200.0,
            horizontal_load_x=10.0,
            horizontal_load_y=0.0,
        )
        bc_factors = BearingCapacityFactors(
            nc=1.0,
            nq=18.401,
            ng=1.0,
        )
        phi = 30.0
        cohesion = 10.0

        result = calc_inclination_factors(phi, cohesion, bc_factors, foundation, loads)
        assert abs(result.ic - 0.924) < 1e-3
        assert abs(result.iq - 0.928) < 1e-3
        assert abs(result.ig - 0.886) < 1e-3

    def test_calc_inclination_factors_4(self):
        """Case 4: φ = 30°, c = 10, HL = 10, HB = 0, V = 200"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
            foundation_length=1.5,
            effective_width=1.0,
            effective_length=1.5,
        )

        loads = Loads(
            vertical_load=200.0,
            horizontal_load_x=0.0,
            horizontal_load_y=10.0,
        )
        bc_factors = BearingCapacityFactors(
            nc=1.0,
            nq=18.401,
            ng=1.0,
        )
        phi = 30.0
        cohesion = 10.0

        result = calc_inclination_factors(phi, cohesion, bc_factors, foundation, loads)
        assert abs(result.ic - 0.933) < 1e-3
        assert abs(result.iq - 0.937) < 1e-3
        assert abs(result.ig - 0.894) < 1e-3

    def test_calc_inclination_factors_5(self):
        """Case 5: φ = 30°, c = 10, HL = 10, HB = 10, V = 200"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
            foundation_length=1.5,
            effective_width=1.0,
            effective_length=1.5,
        )

        loads = Loads(
            vertical_load=200.0,
            horizontal_load_x=10.0,
            horizontal_load_y=10.0,
        )
        bc_factors = BearingCapacityFactors(
            nc=1.0,
            nq=18.401,
            ng=1.0,
        )
        phi = 30.0
        cohesion = 10.0

        result = calc_inclination_factors(phi, cohesion, bc_factors, foundation, loads)
        assert abs(result.ic - 0.805) < 1e-3
        assert abs(result.iq - 0.817) < 1e-3
        assert abs(result.ig - 0.742) < 1e-3


class TestCalcDepthFactors:
    """Test cases for calc_depth_factors function."""

    def test_calc_depth_factors_1(self):
        """Case 1: φ = 0°, Df/B = 1"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
        )

        phi = 0.0
        result = calc_depth_factors(foundation, phi)
        assert abs(result.dc - 0.4) < 1e-3
        assert abs(result.dq - 1.0) < 1e-3
        assert abs(result.dg - 1.0) < 1e-3

    def test_calc_depth_factors_2(self):
        """Case 2: φ = 30°, Df/B = 1"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=1.0,
        )

        phi = 30.0
        result = calc_depth_factors(foundation, phi)
        assert abs(result.dc - 1.4) < 1e-3
        assert abs(result.dq - 1.289) < 1e-3
        assert abs(result.dg - 1.0) < 1e-3

    def test_calc_depth_factors_3(self):
        """Case 3: φ = 0°, Df/B > 1"""
        foundation = Foundation(
            foundation_depth=2.0,
            foundation_width=1.0,
        )

        phi = 0.0
        result = calc_depth_factors(foundation, phi)
        assert abs(result.dc - 0.013957) < 1e-3
        assert abs(result.dq - 1.0) < 1e-3
        assert abs(result.dg - 1.0) < 1e-3

    def test_calc_depth_factors_4(self):
        """Case 4: φ = 30°, Df/B > 1"""
        foundation = Foundation(
            foundation_depth=2.0,
            foundation_width=1.0,
        )

        phi = 30.0
        result = calc_depth_factors(foundation, phi)
        assert abs(result.dc - 1.013957) < 1e-3
        assert abs(result.dq - 1.010073) < 1e-3
        assert abs(result.dg - 1.0) < 1e-3


class TestCalcBaseFactors:
    """Test cases for calc_base_factors function."""

    def test_calc_base_factors_1(self):
        """Case 1: φ = 0°, slope = 0°, base = 0°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=2.0,
            foundation_length=2.0,
            base_tilt_angle=0.0,
            slope_angle=0.0,
        )
        phi = 0.0
        result = calc_base_factors(phi, foundation)

        assert abs(result.bc - 0.0) < 1e-3
        assert abs(result.bq - 1.0) < 1e-3
        assert abs(result.bg - 1.0) < 1e-3

    def test_calc_base_factors_2(self):
        """Case 2: φ = 30°, slope = 0°, base = 0°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=2.0,
            foundation_length=2.0,
            base_tilt_angle=0.0,
            slope_angle=0.0,
        )
        phi = 30.0
        result = calc_base_factors(phi, foundation)

        assert abs(result.bc - 1.0) < 1e-3
        assert abs(result.bq - 1.0) < 1e-3
        assert abs(result.bg - 1.0) < 1e-3

    def test_calc_base_factors_3(self):
        """Case 3: φ = 0°, slope = 10°, base = 0°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=2.0,
            foundation_length=2.0,
            base_tilt_angle=0.0,
            slope_angle=10.0,
        )
        phi = 0.0
        result = calc_base_factors(phi, foundation)

        assert abs(result.bc - 0.034) < 1e-3
        assert abs(result.bq - 1.0) < 1e-3
        assert abs(result.bg - 1.0) < 1e-3

    def test_calc_base_factors_4(self):
        """Case 4: φ = 0°, slope = 0°, base = 10°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=2.0,
            foundation_length=2.0,
            base_tilt_angle=10.0,
            slope_angle=0.0,
        )
        phi = 0.0
        result = calc_base_factors(phi, foundation)

        assert abs(result.bc - 0.0) < 1e-3
        assert abs(result.bq - 1.0) < 1e-3
        assert abs(result.bg - 1.0) < 1e-3

    def test_calc_base_factors_5(self):
        """Case 5: φ = 0°, slope = 10°, base = 10°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=2.0,
            foundation_length=2.0,
            base_tilt_angle=10.0,
            slope_angle=10.0,
        )
        phi = 0.0
        result = calc_base_factors(phi, foundation)

        assert abs(result.bc - 0.034) < 1e-3
        assert abs(result.bq - 1.0) < 1e-3
        assert abs(result.bg - 1.0) < 1e-3

    def test_calc_base_factors_6(self):
        """Case 6: φ = 30°, slope = 10°, base = 10°"""
        foundation = Foundation(
            foundation_depth=1.0,
            foundation_width=2.0,
            foundation_length=2.0,
            base_tilt_angle=10.0,
            slope_angle=10.0,
        )
        phi = 30.0
        result = calc_base_factors(phi, foundation)

        assert abs(result.bc - 0.882) < 1e-3
        assert abs(result.bq - 0.809) < 1e-3
        assert abs(result.bg - 0.809) < 1e-3


class TestCalcGroundFactors:
    """Test cases for calc_ground_factors function."""

    def test_calc_ground_factors_1(self):
        """Case 1: φ = 0°, slope = 0°"""
        phi = 0.0
        slope = 0.0
        iq = 1.0
        result = calc_ground_factors(iq, slope, phi)
        assert abs(result.gc - 0.0) < 1e-3
        assert abs(result.gq - 1.0) < 1e-3
        assert abs(result.gg - 1.0) < 1e-3

    def test_calc_ground_factors_2(self):
        """Case 2: φ = 30°, slope = 0°"""
        phi = 30.0
        slope = 0.0
        iq = 0.861
        result = calc_ground_factors(iq, slope, phi)
        assert abs(result.gc - 0.814) < 1e-3
        assert abs(result.gq - 1.0) < 1e-3
        assert abs(result.gg - 1.0) < 1e-3

    def test_calc_ground_factors_3(self):
        """Case 3: φ = 0°, slope = 5°"""
        phi = 0.0
        slope = 5.0
        iq = 1.0
        result = calc_ground_factors(iq, slope, phi)
        assert abs(result.gc - 0.017) < 1e-3
        assert abs(result.gq - 0.833) < 1e-3
        assert abs(result.gg - 0.833) < 1e-3

    def test_calc_ground_factors_4(self):
        """Case 4: φ = 30°, slope = 5°"""
        phi = 30.0
        slope = 5.0
        iq = 0.861
        result = calc_ground_factors(iq, slope, phi)
        assert abs(result.gc - 0.814) < 1e-3
        assert abs(result.gq - 0.833) < 1e-3
        assert abs(result.gg - 0.833) < 1e-3
