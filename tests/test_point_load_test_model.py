"""Tests for Point Load Test model methods."""

import pytest

from soilpy.enums import SelectionMethod
from soilpy.models.point_load_test import PointLoadExp, PointLoadSample, PointLoadTest


class TestPointLoadTestModel:
    """Test cases for Point Load Test model methods."""

    def create_test_data(self) -> PointLoadTest:
        """Create test Point Load Test data."""
        sk1 = PointLoadExp.new(
            "Borehole1",
            [
                PointLoadSample.new(1.5, 2.67, 50.0),
                PointLoadSample.new(3.0, 2.38, 50.0),
            ],
        )
        sk2 = PointLoadExp.new(
            "Borehole2",
            [
                PointLoadSample.new(1.5, 2.66, 50.0),
                PointLoadSample.new(3.0, 2.96, 50.0),
            ],
        )
        sk3 = PointLoadExp.new(
            "Borehole3",
            [
                PointLoadSample.new(3.0, 2.53, 50.0),
                PointLoadSample.new(4.5, 2.84, 50.0),
            ],
        )

        return PointLoadTest.new([sk1, sk2, sk3], SelectionMethod.MIN)

    def test_get_sample_at_depth_1(self):
        """Test sample retrieval at exact depth."""
        exp = self.create_test_data().exps[0]

        sample = exp.get_sample_at_depth(1.5)
        assert sample.depth == 1.5
        assert sample.is50 == 2.67

    def test_get_sample_at_depth_2(self):
        """Test sample retrieval at intermediate depth."""
        exp = self.create_test_data().exps[0]

        sample = exp.get_sample_at_depth(2.0)
        assert sample.depth == 3.0
        assert sample.is50 == 2.38

    def test_get_sample_at_depth_3(self):
        """Test sample retrieval at depth exceeding all samples."""
        exp = self.create_test_data().exps[0]

        sample = exp.get_sample_at_depth(4.0)
        assert sample.depth == 3.0
        assert sample.is50 == 2.38

    def test_get_idealized_exp_min_mode(self):
        """Test idealized experiment creation in MIN mode."""
        data = self.create_test_data()

        ideal = data.get_idealized_exp("Ideal_Min")

        # Sanity checks
        assert ideal.borehole_id == "Ideal_Min"

        # Should be based on union of depths: [1.5, 3.0, 4.5]
        assert len(ideal.samples) == 3

        # Check first layer values
        layer1 = ideal.samples[0]
        assert abs(layer1.depth - 1.5) < 1e-6
        assert abs(layer1.is50 - 2.66) < 1e-6
        assert abs(layer1.d - 50.0) < 1e-6

        # Check second layer values
        layer2 = ideal.samples[1]
        assert abs(layer2.depth - 3.0) < 1e-6
        assert abs(layer2.is50 - 2.38) < 1e-6
        assert abs(layer2.d - 50.0) < 1e-6

        # Check last layer depth
        last_layer = ideal.samples[-1]
        assert abs(last_layer.depth - 4.5) < 1e-6

    def test_get_idealized_exp_avg_mode(self):
        """Test idealized experiment creation in AVG mode."""
        data = self.create_test_data()

        data.idealization_method = SelectionMethod.AVG
        ideal = data.get_idealized_exp("Ideal_Avg")

        # Sanity checks
        assert ideal.borehole_id == "Ideal_Avg"

        # Should be based on union of depths: [1.5, 3.0, 4.5]
        assert len(ideal.samples) == 3

        # Check first layer values
        layer1 = ideal.samples[0]
        assert abs(layer1.depth - 1.5) < 1e-6
        assert abs(layer1.is50 - 2.665) < 1e-6
        assert abs(layer1.d - 50.0) < 1e-6

        # Check second layer values
        layer2 = ideal.samples[1]
        assert abs(layer2.depth - 3.0) < 1e-6
        assert abs(layer2.is50 - 2.623) < 1e-3
        assert abs(layer2.d - 50.0) < 1e-6

        # Check last layer depth
        last_layer = ideal.samples[-1]
        assert abs(last_layer.depth - 4.5) < 1e-6

    def test_get_idealized_exp_max_mode(self):
        """Test idealized experiment creation in MAX mode."""
        data = self.create_test_data()

        data.idealization_method = SelectionMethod.MAX
        ideal = data.get_idealized_exp("Ideal_Max")

        # Sanity checks
        assert ideal.borehole_id == "Ideal_Max"

        # Should be based on union of depths: [1.5, 3.0, 4.5]
        assert len(ideal.samples) == 3

        # Check first layer values
        layer1 = ideal.samples[0]
        assert abs(layer1.depth - 1.5) < 1e-6
        assert abs(layer1.is50 - 2.67) < 1e-6
        assert abs(layer1.d - 50.0) < 1e-6

        # Check second layer values
        layer2 = ideal.samples[1]
        assert abs(layer2.depth - 3.0) < 1e-6
        assert abs(layer2.is50 - 2.96) < 1e-3
        assert abs(layer2.d - 50.0) < 1e-6

        # Check last layer depth
        last_layer = ideal.samples[-1]
        assert abs(last_layer.depth - 4.5) < 1e-6
