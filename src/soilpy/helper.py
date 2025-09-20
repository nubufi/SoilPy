"""Helper functions module for SoilPy."""

from typing import List, Union

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def interp1d(x_values: List[float], y_values: List[float], x: float) -> float:
    """Performs linear interpolation for a given x value based on provided x and y vectors.

    Args:
        x_values: Array of x-axis values (must be sorted)
        y_values: Array of y-axis values
        x: The x value for which to interpolate

    Returns:
        Interpolated y value as float

    Raises:
        ValueError: If x_values and y_values lengths are not equal or x is out of range
    """
    if len(x_values) != len(y_values):
        raise ValueError("x_values and y_values must have the same length")

    if not x_values:
        raise ValueError("x_values cannot be empty")

    # Convert to arrays for easier handling
    if HAS_NUMPY:
        x_arr = np.array(x_values)
        y_arr = np.array(y_values)
    else:
        x_arr = x_values
        y_arr = y_values

    # Handle edge cases
    if x <= x_arr[0]:
        return float(y_arr[0])
    if x >= x_arr[-1]:
        return float(y_arr[-1])

    # Find the interpolation interval
    for i in range(len(x_arr) - 1):
        x0, x1 = x_arr[i], x_arr[i + 1]
        y0, y1 = y_arr[i], y_arr[i + 1]

        if x0 <= x <= x1:
            # Linear interpolation
            return float(y0 + (y1 - y0) * (x - x0) / (x1 - x0))

    raise ValueError("Interpolation error: x-value out of interpolation range")
