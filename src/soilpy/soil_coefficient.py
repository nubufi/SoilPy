"""Soil coefficient calculations for SoilPy."""


def calc_by_settlement(settlement: float, foundation_pressure: float) -> float:
    """Calculates the soil coefficient based on settlement and foundation load.
    Returns a high value (999_999.0) if settlement is zero or negative to avoid division by zero.

    Args:
        settlement: The settlement of the foundation in meters
        foundation_pressure: The load on the foundation in tons

    Returns:
        The soil coefficient in tons per cubic meter (t/m³)
    """
    if settlement <= 0.0:
        return 999_999.0
    return 100.0 * foundation_pressure / settlement  # units: t/m³


def calc_by_bearing_capacity(bearing_capacity: float) -> float:
    """Calculates the soil coefficient based on bearing capacity.
    Uses a factor of 400 as specified in empirical design practice.

    Args:
        bearing_capacity: The bearing capacity of the soil in tons per square meter (t/m²)

    Returns:
        The soil coefficient in tons per cubic meter (t/m³)
    """
    return 400.0 * bearing_capacity  # units: t/m³
