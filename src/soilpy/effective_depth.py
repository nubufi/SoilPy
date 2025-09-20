"""Effective depth calculations for SoilPy."""

from soilpy.models import Foundation, SoilProfile
from soilpy.validation import ValidationError, validate_field


def validate_input(
    soil_profile: SoilProfile,
    foundation: Foundation,
    foundation_pressure: float,
) -> None:
    """Validates the input data for elastic settlement calculations.

    Args:
        soil_profile: The soil profile data
        foundation: The foundation data
        foundation_pressure: The foundation pressure (q) [t/m²]

    Raises:
        ValidationError: If validation fails
    """
    soil_profile.validate(["thickness", "dry_unit_weight", "saturated_unit_weight"])
    foundation.validate(["foundation_depth", "foundation_width", "foundation_length"])

    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )


def get_difference(z: float, f: float, b: float, df: float, l: float, sp: SoilProfile) -> float:
    """Calculates the difference between the stress increment (Δσ) and 10% of effective stress at depth z.

    Args:
        z: Depth
        f: Net foundation force
        b: Foundation width
        df: Foundation depth
        l: Foundation length
        sp: Soil profile

    Returns:
        The difference between stress increment and 10% of effective stress
    """
    dg = f / ((b + z - df) * (l + z - df))
    effective_stress = sp.calc_effective_stress(z)
    return dg - 0.1 * effective_stress


def find_effective_depth(f: float, b: float, df: float, l: float, sp: SoilProfile) -> float:
    """Finds the effective depth where the stress increment equals 10% of effective stress using the bisection method.

    Args:
        f: Net foundation force
        b: Foundation width
        df: Foundation depth
        l: Foundation length
        sp: Soil profile

    Returns:
        The effective depth in meters
    """
    boundary1 = df
    boundary2 = df + 1.5 * b
    middle = (boundary1 + boundary2) / 2.0
    n = 0

    # Check if both ends have same sign, then widen the boundary
    if (
        get_difference(boundary1, f, b, df, l, sp) * get_difference(boundary2, f, b, df, l, sp)
        > 0.0
    ):
        boundary2 = 100.0 * b

    # Bisection loop
    while abs(get_difference(middle, f, b, df, l, sp)) > 0.01 and n < 100:
        n += 1
        if boundary1 == boundary2 == middle and n > 10:
            return 0.0

        if get_difference(middle, f, b, df, l, sp) > 0.0:
            boundary1 = middle
        else:
            boundary2 = middle

        middle = (boundary1 + boundary2) / 2.0

    return middle


def calc_effective_depth(
    soil_profile: SoilProfile,
    foundation_data: Foundation,
    foundation_pressure: float,
) -> float:
    """Public function to calculate effective depth based on foundation and soil data.

    Args:
        soil_profile: A reference to a SoilProfile object
        foundation_data: A reference to a Foundation object
        foundation_pressure: The pressure applied by the foundation in ton/m2

    Returns:
        The effective depth as a float value in meters

    Raises:
        ValidationError: If validation fails
    """
    validate_input(soil_profile, foundation_data, foundation_pressure)

    if foundation_data.foundation_depth is None:
        raise ValueError("Foundation depth must be set")
    if foundation_data.foundation_width is None:
        raise ValueError("Foundation width must be set")
    if foundation_data.foundation_length is None:
        raise ValueError("Foundation length must be set")

    df = foundation_data.foundation_depth
    b = foundation_data.foundation_width
    l = foundation_data.foundation_length

    q_net = foundation_pressure - soil_profile.calc_normal_stress(df)
    f = q_net * b * l

    result = find_effective_depth(f, b, df, l, soil_profile)

    return result
