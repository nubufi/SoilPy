"""Tests for CPT (Cone Penetration Test) functions."""

import pytest

from soilpy.enums import SelectionMethod
from soilpy.models.cpt import CPT, CPTExp, CPTLayer


class TestCPTLayer:
    """Test cases for CPTLayer methods."""

    def test_calc_friction_ratio_valid(self):
        """Test friction ratio calculation with valid values."""
        layer = CPTLayer.new(1.0, 10.0, 0.5, 0.2)
        layer.calc_friction_ratio()
        assert layer.friction_ratio is not None
        rf = layer.friction_ratio
        assert abs(rf - 5.0) < 1e-6  # 0.5 / 10.0 * 100 = 5.0%

    def test_calc_friction_ratio_zero_cone_resistance(self):
        """Test friction ratio calculation with zero cone resistance."""
        layer = CPTLayer.new(1.0, 0.0, 0.5, 0.2)
        layer.calc_friction_ratio()
        assert layer.friction_ratio is None


class TestCPTExp:
    """Test cases for CPTExp methods."""

    def create_test_layers(self):
        """Create test layers for testing."""
        return [
            CPTLayer.new(1.0, 10.0, 0.5, 0.2),
            CPTLayer.new(2.0, 11.0, 0.6, 0.3),
            CPTLayer.new(3.0, 12.0, 0.7, 0.4),
        ]

    def test_get_layer_at_exact_depth(self):
        """Test getting layer at exact depth."""
        layers = self.create_test_layers()
        cpt = CPTExp.new(layers, "Test CPT")

        layer = cpt.get_layer_at_depth(2.0)
        assert layer.depth == 2.0

    def test_get_layer_at_intermediate_depth(self):
        """Test getting layer at intermediate depth."""
        layers = self.create_test_layers()
        cpt = CPTExp.new(layers, "Test CPT")

        layer = cpt.get_layer_at_depth(2.5)
        assert layer.depth == 3.0

    def test_get_layer_at_depth_exceeds_all_layers(self):
        """Test getting layer when depth exceeds all layers."""
        layers = self.create_test_layers()
        cpt = CPTExp.new(layers, "Test CPT")

        layer = cpt.get_layer_at_depth(5.0)
        assert layer.depth == 3.0  # last layer

    def test_get_layer_with_empty_layers_should_raise_error(self):
        """Test getting layer with empty layers should raise error."""
        cpt = CPTExp.new([], "Empty CPT")
        # In Python, this will return an empty CPTLayer instead of panicking
        layer = cpt.get_layer_at_depth(1.0)
        assert layer.depth is None


class TestCPT:
    """Test cases for CPT methods."""

    def create_test_cpt(self):
        """Create test CPT for testing."""
        exp1 = CPTExp.new(
            [
                CPTLayer.new(1.5, 160.0, 390.0, None),
                CPTLayer.new(2.0, 170.0, 395.0, None),
                CPTLayer.new(3.0, 180.0, 400.0, None),
            ],
            "Exp1",
        )

        exp2 = CPTExp.new(
            [
                CPTLayer.new(1.5, 150.0, 380.0, None),
                CPTLayer.new(3.0, 160.0, 390.0, None),
                CPTLayer.new(5.5, 170.0, 395.0, None),
                CPTLayer.new(6.5, 180.0, 400.0, None),
            ],
            "Exp2",
        )

        return CPT.new([exp1, exp2], SelectionMethod.MIN)

    def test_get_idealized_exp_min_mode(self):
        """Test idealized experiment with MIN mode."""
        cpt = self.create_test_cpt()

        ideal = cpt.get_idealized_exp("Ideal_Min")

        # Sanity checks
        assert ideal.name == "Ideal_Min"

        # Should be based on union of depths: [1.5, 2.0, 3.0, 5.5, 6.5]
        assert len(ideal.layers) == 5

        # Check first layer values
        layer1 = ideal.layers[0]
        assert abs(layer1.depth - 1.5) < 1e-6
        assert abs(layer1.cone_resistance - 150.0) < 1e-6
        assert abs(layer1.sleeve_friction - 380.0) < 1e-6

        # Check last layer depth
        last_layer = ideal.layers[-1]
        assert abs(last_layer.depth - 6.5) < 1e-6

    def test_get_idealized_exp_avg_mode(self):
        """Test idealized experiment with AVG mode."""
        cpt = self.create_test_cpt()
        cpt.idealization_method = SelectionMethod.AVG
        ideal = cpt.get_idealized_exp("Ideal_Avg")

        # Sanity checks
        assert ideal.name == "Ideal_Avg"

        # Should be based on union of depths: [1.5, 2.0, 3.0, 5.5, 6.5]
        assert len(ideal.layers) == 5

        # Check first layer values
        layer1 = ideal.layers[0]
        assert abs(layer1.depth - 1.5) < 1e-6
        assert abs(layer1.cone_resistance - 155.0) < 1e-6
        assert abs(layer1.sleeve_friction - 385.0) < 1e-6

        # Check last layer depth
        last_layer = ideal.layers[-1]
        assert abs(last_layer.depth - 6.5) < 1e-6

    def test_get_idealized_exp_max_mode(self):
        """Test idealized experiment with MAX mode."""
        cpt = self.create_test_cpt()
        cpt.idealization_method = SelectionMethod.MAX
        ideal = cpt.get_idealized_exp("Ideal_Max")

        # Sanity checks
        assert ideal.name == "Ideal_Max"

        # Should be based on union of depths: [1.5, 2.0, 3.0, 5.5, 6.5]
        assert len(ideal.layers) == 5

        # Check first layer values
        layer1 = ideal.layers[0]
        assert abs(layer1.depth - 1.5) < 1e-6
        assert abs(layer1.cone_resistance - 160.0) < 1e-6
        assert abs(layer1.sleeve_friction - 390.0) < 1e-6

        # Check last layer depth
        last_layer = ideal.layers[-1]
        assert abs(last_layer.depth - 6.5) < 1e-6
