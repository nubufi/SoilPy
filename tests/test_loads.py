"""Tests for Loads model methods."""

import pytest

from soilpy.enums import LoadCase, SelectionMethod
from soilpy.models.loads import Loads, Stress


class TestLoads:
    """Test cases for Loads model methods."""

    def test_calc_eccentricity(self):
        """Test eccentricity calculation with normal loads."""
        loading = Loads(
            vertical_load=10.0,
            moment_x=20.0,
            moment_y=15.0,
        )

        ex, ey = loading.calc_eccentricity()

        assert abs(ex - 2.0) < 1e-6
        assert abs(ey - 1.5) < 1e-6

    def test_calc_eccentricity_zero_load(self):
        """Test eccentricity calculation with zero vertical load."""
        loading = Loads(
            moment_x=20.0,
            moment_y=15.0,
        )

        ex, ey = loading.calc_eccentricity()

        assert ex == 0.0
        assert ey == 0.0

    def test_get_vertical_stress(self):
        """Test vertical stress retrieval for different load cases and selection methods."""
        # Create a struct with known values
        stress_data = Loads(
            service_load=Stress(
                min=10.0,
                avg=15.0,
                max=20.0,
            ),
            ultimate_load=Stress(
                min=25.0,
                avg=30.0,
                max=35.0,
            ),
            seismic_load=Stress(
                min=40.0,
                avg=45.0,
                max=None,
            ),
        )

        # Test Service Load
        assert stress_data.get_vertical_stress(LoadCase.SERVICE_LOAD, SelectionMethod.MIN) == 10.0
        assert stress_data.get_vertical_stress(LoadCase.SERVICE_LOAD, SelectionMethod.AVG) == 15.0
        assert stress_data.get_vertical_stress(LoadCase.SERVICE_LOAD, SelectionMethod.MAX) == 20.0

        # Test Ultimate Load
        assert stress_data.get_vertical_stress(LoadCase.ULTIMATE_LOAD, SelectionMethod.MIN) == 25.0
        assert stress_data.get_vertical_stress(LoadCase.ULTIMATE_LOAD, SelectionMethod.AVG) == 30.0
        assert stress_data.get_vertical_stress(LoadCase.ULTIMATE_LOAD, SelectionMethod.MAX) == 35.0

        # Test Seismic Load
        assert stress_data.get_vertical_stress(LoadCase.SEISMIC_LOAD, SelectionMethod.MIN) == 40.0
        assert stress_data.get_vertical_stress(LoadCase.SEISMIC_LOAD, SelectionMethod.AVG) == 45.0
        assert stress_data.get_vertical_stress(LoadCase.SEISMIC_LOAD, SelectionMethod.MAX) == 0.0
