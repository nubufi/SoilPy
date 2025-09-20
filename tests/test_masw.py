"""Tests for MASW model methods."""

import pytest

from soilpy.enums import SelectionMethod
from soilpy.models.masw import Masw, MaswExp, MaswLayer


class TestMasw:
    """Test cases for MASW model methods."""

    def test_calc_depths(self):
        """Test depth calculation for MASW experiment layers."""
        layers = [
            MaswLayer.new(1.5, 1.0, 1.0),
            MaswLayer.new(2.5, 1.0, 1.0),
            MaswLayer.new(4.0, 1.0, 1.0),
        ]

        masw_exp = MaswExp(
            layers=layers,
            name="Test",
        )
        masw_exp.calc_depths()

        assert masw_exp.layers[0].depth == 1.5
        assert masw_exp.layers[1].depth == 4.0
        assert masw_exp.layers[2].depth == 8.0

    def test_calc_depths_invalid_thickness(self):
        """Test depth calculation with invalid thickness (should raise ValueError)."""
        layers = [
            MaswLayer.new(3.0, 1.0, 1.0),
            MaswLayer.new(0.0, 1.0, 1.0),  # This should trigger a ValueError
        ]

        with pytest.raises(
            ValueError, match="Thickness of MASW experiment must be greater than zero."
        ):
            MaswExp.new(layers, "Test")

    def test_get_layer_at_depth(self):
        """Test layer retrieval at specific depths."""
        layers = [
            MaswLayer.new(2.0, 1.0, 1.0),
            MaswLayer.new(3.0, 2.0, 2.0),
            MaswLayer.new(5.0, 3.0, 3.0),
        ]

        masw_exp = MaswExp.new(layers, "Test")

        layer = masw_exp.get_layer_at_depth(4.0)
        assert layer.vs == 2.0  # The second layer should be returned

        layer = masw_exp.get_layer_at_depth(15.0)
        assert layer.vs == 3.0

    def create_test_masw(self) -> Masw:
        """Create test MASW data for idealization tests."""
        exp1 = MaswExp.new(
            [
                MaswLayer.new(2.0, 180.0, 400.0),  # depth: 2.0
                MaswLayer.new(3.0, 200.0, 450.0),  # depth: 5.0
            ],
            "Exp1",
        )

        exp2 = MaswExp.new(
            [
                MaswLayer.new(1.5, 170.0, 390.0),  # depth: 1.5
                MaswLayer.new(4.0, 190.0, 430.0),  # depth: 5.5
            ],
            "Exp2",
        )

        exp3 = MaswExp.new(
            [
                MaswLayer.new(3.0, 160.0, 395.0),  # depth: 3.0
                MaswLayer.new(3.0, 180.0, 420.0),  # depth: 6.0
            ],
            "Exp3",
        )

        return Masw.new([exp1, exp2, exp3], SelectionMethod.MIN)

    def test_get_idealized_exp_min_mode(self):
        """Test idealized experiment creation in MIN mode."""
        masw = self.create_test_masw()

        ideal = masw.get_idealized_exp("Ideal_Min")

        # Sanity checks
        assert ideal.name == "Ideal_Min"

        # Should be based on union of depths: [1.5, 2.0, 3.0, 5.0, 5.5, 6.0]
        assert len(ideal.layers) == 6

        # Check first layer values
        layer1 = ideal.layers[0]
        assert layer1.thickness == 1.5
        assert layer1.vs == 160.0
        assert layer1.vp == 390.0

        # Check last layer depth
        last_layer = ideal.layers[-1]
        assert last_layer.depth == 6.0

    def test_get_idealized_exp_avg_mode(self):
        """Test idealized experiment creation in AVG mode."""
        masw = self.create_test_masw()

        masw.idealization_method = SelectionMethod.AVG
        ideal = masw.get_idealized_exp("Ideal_Avg")

        # Sanity checks
        assert ideal.name == "Ideal_Avg"

        # Should be based on union of depths: [1.5, 2.0, 3.0, 5.0, 5.5, 6.0]
        assert len(ideal.layers) == 6

        # Check first layer values
        layer1 = ideal.layers[0]
        assert layer1.thickness == 1.5
        assert layer1.vs == 170.0
        assert layer1.vp == 395.0

        # Check last layer depth
        last_layer = ideal.layers[-1]
        assert last_layer.depth == 6.0

    def test_get_idealized_exp_max_mode(self):
        """Test idealized experiment creation in MAX mode."""
        masw = self.create_test_masw()

        masw.idealization_method = SelectionMethod.MAX
        ideal = masw.get_idealized_exp("Ideal_Max")

        # Sanity checks
        assert ideal.name == "Ideal_Max"

        # Should be based on union of depths: [1.5, 2.0, 3.0, 5.0, 5.5, 6.0]
        assert len(ideal.layers) == 6

        # Check first layer values
        layer1 = ideal.layers[0]
        assert layer1.thickness == 1.5
        assert layer1.vs == 180.0
        assert layer1.vp == 400.0

        # Check last layer depth
        last_layer = ideal.layers[-1]
        assert last_layer.depth == 6.0
