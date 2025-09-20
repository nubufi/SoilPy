"""Tests for Point Load Test bearing capacity calculations."""

import pytest

from soilpy.bearing_capacity.point_load_test import (
    calc_bearing_capacity,
    get_generalized_c_value,
)
from soilpy.enums import SelectionMethod
from soilpy.models.foundation import Foundation
from soilpy.models.point_load_test import PointLoadExp, PointLoadSample, PointLoadTest


class TestGetGeneralizedCValue:
    """Test cases for get_generalized_c_value function."""

    def test_get_generalized_c_value(self):
        """Test cases for the generalized size correction factor C"""
        test_cases = [(10.0, 17.5), (30.0, 19.0), (45.0, 22.0), (65.0, 24.5)]

        for d, expected_c in test_cases:
            c = get_generalized_c_value(d)
            assert abs(c - expected_c) < 1e-10, f"Failed for d = {d}"


class TestCalcBearingCapacity:
    """Test cases for calc_bearing_capacity function."""

    def test_calc_bearing_capacity(self):
        """Test bearing capacity calculation with point load test data"""
        exp = PointLoadExp.new("Test", [PointLoadSample.new(20.0, 2.0, 50.0)])
        pt = PointLoadTest.new([exp], SelectionMethod.MIN)

        foundation_pressure = 100.0
        safety_factor = 2.0
        foundation = Foundation(foundation_depth=20.0)

        result = calc_bearing_capacity(pt, foundation, foundation_pressure, safety_factor)

        assert result.c == 23.0
        assert abs(result.ucs - 4690.69452) < 1e-5
        assert abs(result.allowable_bearing_capacity - 2345.34726) < 1e-5
