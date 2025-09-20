"""Tests for Foundation model methods."""

import pytest

from soilpy.models.foundation import Foundation


class TestFoundation:
    """Test cases for Foundation model methods."""

    def test_calc_effective_lengths(self):
        """Test effective lengths calculation with eccentricity."""
        foundation = Foundation(
            foundation_length=10.0,
            foundation_width=5.0,
        )

        ex = 1.0  # Eccentricity in x-direction (m)
        ey = 1.5  # Eccentricity in y-direction (m)

        foundation.calc_effective_lengths(ex, ey)

        # Expected values:
        # b' = 5 - 2 * 1.0 = 3.0
        # l' = 10 - 2 * 1.5 = 7.0
        # effective_width = min(3.0, 7.0) = 3.0
        # effective_length = max(3.0, 7.0) = 7.0
        assert foundation.effective_width == 3.0
        assert foundation.effective_length == 7.0

    def test_calc_effective_lengths_zero_eccentricity(self):
        """Test effective lengths calculation with zero eccentricity."""
        foundation = Foundation(
            foundation_length=8.0,
            foundation_width=4.0,
        )

        foundation.calc_effective_lengths(0.0, 0.0)

        # No eccentricity, so effective dimensions should remain the same
        assert foundation.effective_width == 4.0
        assert foundation.effective_length == 8.0

    def test_calc_effective_lengths_negative_effective_size(self):
        """Test effective lengths calculation with large eccentricity."""
        foundation = Foundation(
            foundation_length=6.0,
            foundation_width=3.0,
        )

        ex = 2.0  # Large eccentricity causing negative width
        ey = 2.0  # Large eccentricity causing negative length

        foundation.calc_effective_lengths(ex, ey)

        # Negative values should be prevented (width or length cannot be negative)
        assert foundation.effective_width == 0.0
        assert foundation.effective_length == 2.0  # The remaining length
