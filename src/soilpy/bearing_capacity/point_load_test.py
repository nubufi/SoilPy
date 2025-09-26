"""Point Load Test bearing capacity calculations for SoilPy."""

from typing import Optional

from pydantic import BaseModel

from soilpy.models import Foundation, PointLoadTest
from soilpy.validation import ValidationError, validate_field


class Output(BaseModel):
    """Represents the bearing capacity result for a given soil and foundation setup."""

    is50: float  # Is50 value in MPa
    ucs: float  # Uniaxial compressive strength (UCS) in MPa
    c: float  # Generalized value of C
    d: float  # Equivalent core diameter in mm
    allowable_bearing_capacity: float  # Allowable bearing capacity in ton/m2
    qmax: float  # The pressure exerted by the foundation in ton/m2
    df: float  # Indicates the depth at which the bearing capacity is calculated in meters
    is_safe: bool  # Indicates whether the bearing capacity is safe
    safety_factor: float  # Safety factor used in the design


def validate_input(
    point_load_test: PointLoadTest,
    foundation: Foundation,
    foundation_pressure: float,
    safety_factor: float,
) -> None:
    """Validates the input data for point load test bearing capacity calculations.

    Args:
        point_load_test: The point load test data
        foundation: The foundation data
        foundation_pressure: The foundation pressure
        safety_factor: The safety factor

    Raises:
        ValidationError: If validation fails
    """
    point_load_test.validate(["is50", "d"])
    foundation.validate(["foundation_depth"])
    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )
    validate_field(
        "safety_factor",
        safety_factor,
        1.0,
        error_code_prefix="safety_factor",
    )


def get_generalized_c_value(d: float) -> float:
    """Calculates the generalized size correction factor C based on the given equivalent core diameter D.

    This follows the standard chart provided by ASTM and ISRM guidelines for point load tests,
    interpolating intermediate values.

    Args:
        d: Sample diameter in millimeters (mm)

    Returns:
        The generalized correction factor C
    """
    # Diameter (mm) to C values mapping
    diameters = [
        (20.0, 17.5),
        (30.0, 19.0),
        (40.0, 21.0),
        (50.0, 23.0),
        (54.0, 24.0),
        (60.0, 24.5),
    ]

    if d <= diameters[0][0]:
        return diameters[0][1]

    if d >= diameters[-1][0]:
        return diameters[-1][1]

    # Interpolate intermediate values
    for i in range(len(diameters) - 1):
        d_lower, c_lower = diameters[i]
        d_upper, c_upper = diameters[i + 1]

        if d_lower <= d <= d_upper:
            fraction = (d - d_lower) / (d_upper - d_lower)
            return c_lower + fraction * (c_upper - c_lower)

    # This should never be reached due to the bounds check above
    return diameters[-1][1]


def calc_bearing_capacity(
    point_load_test: PointLoadTest,
    foundation: Foundation,
    foundation_pressure: float,
    safety_factor: float,
) -> Output:
    """Calculates the bearing capacity of a foundation based on point load test results.

    Args:
        point_load_test: The point load test data
        foundation: The foundation data
        foundation_pressure: The pressure exerted by the foundation
        safety_factor: The safety factor for the design

    Returns:
        Output: The bearing capacity result containing various parameters

    Raises:
        ValidationError: If validation fails
    """
    validate_input(point_load_test, foundation, foundation_pressure, safety_factor)

    df = foundation.foundation_depth
    if df is None:
        raise ValueError("Foundation depth must be set")

    point_load_test_exp = point_load_test.get_idealized_exp("idealized")
    MPA_TO_TON = 101.97162  # Conversion factor from MPa to ton/m2
    sample = point_load_test_exp.get_sample_at_depth(df)

    is50 = sample.is50
    d = sample.d
    if is50 is None or d is None:
        raise ValueError("Sample is50 and d values must be set")

    c = get_generalized_c_value(d)
    ucs = is50 * c * MPA_TO_TON
    allowable_bearing_capacity = ucs / safety_factor
    is_safe = allowable_bearing_capacity >= foundation_pressure

    return Output(
        is50=is50,
        ucs=ucs,
        c=c,
        d=d,
        allowable_bearing_capacity=allowable_bearing_capacity,
        is_safe=is_safe,
        safety_factor=safety_factor,
        qmax=foundation_pressure,
        df=df,
    )
