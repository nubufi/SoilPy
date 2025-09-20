"""Horizontal sliding calculations for SoilPy."""

import math
from dataclasses import dataclass

from soilpy.models import Foundation, Loads, SoilProfile
from soilpy.validation import ValidationError, validate_field


@dataclass
class HorizontalSlidingResult:
    """Result of horizontal sliding calculations."""

    rth: float  # Resistance from friction/cohesion
    ptv: float  # Total vertical pressure
    rpk_x: float  # Passive resistance in x direction
    rpk_y: float  # Passive resistance in y direction
    rpt_x: float  # Reduced passive resistance in x direction
    rpt_y: float  # Reduced passive resistance in y direction
    sum_x: float  # Total resistance in x direction
    sum_y: float  # Total resistance in y direction
    is_safe_x: bool  # Safety check in x direction
    is_safe_y: bool  # Safety check in y direction
    ac: float  # Foundation area
    vth_x: float  # Horizontal load in x direction
    vth_y: float  # Horizontal load in y direction


def validate_input(
    soil_profile: SoilProfile,
    foundation: Foundation,
    loads: Loads,
    foundation_pressure: float,
) -> None:
    """Validates the input data for horizontal sliding calculations.

    Args:
        soil_profile: The soil profile data
        foundation: The foundation data
        loads: The load data
        foundation_pressure: The foundation pressure (q) [t/m²]

    Raises:
        ValidationError: If validation fails
    """
    soil_profile.validate(
        [
            "thickness",
            "dry_unit_weight",
            "saturated_unit_weight",
            "c_prime",
            "cu",
            "phi_prime",
            "phi_u",
        ]
    )
    foundation.validate(
        [
            "foundation_depth",
            "foundation_width",
            "foundation_length",
            "surface_friction_coefficient",
        ]
    )
    loads.validate(["horizontal_load_x", "horizontal_load_y"])

    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )


def get_soil_params(soil_profile: SoilProfile, df: float) -> tuple[float, float, float]:
    """Extracts cohesion, friction angle, and unit weight based on groundwater level and soil properties.

    Args:
        soil_profile: The soil profile
        df: Foundation depth

    Returns:
        Tuple of (cohesion, friction_angle, unit_weight)
    """
    layer = soil_profile.get_layer_at_depth(df)

    if layer.c_prime is None:
        raise ValueError("c_prime must be set")
    if layer.cu is None:
        raise ValueError("cu must be set")
    if layer.phi_prime is None:
        raise ValueError("phi_prime must be set")
    if layer.phi_u is None:
        raise ValueError("phi_u must be set")
    if layer.dry_unit_weight is None:
        raise ValueError("dry_unit_weight must be set")
    if layer.saturated_unit_weight is None:
        raise ValueError("saturated_unit_weight must be set")
    if soil_profile.ground_water_level is None:
        raise ValueError("ground_water_level must be set")

    c_prime = layer.c_prime
    cu = layer.cu
    phi_prime = layer.phi_prime
    phi_u = layer.phi_u
    dry_unit_weight = layer.dry_unit_weight
    saturated_unit_weight = layer.saturated_unit_weight

    if soil_profile.ground_water_level <= df:
        selected_unit_weight = saturated_unit_weight - 1.0
        selected_cohesion = cu
        selected_phi = phi_u
    else:
        selected_unit_weight = dry_unit_weight
        selected_cohesion = c_prime
        selected_phi = phi_prime

    return (selected_cohesion, selected_phi, selected_unit_weight)


def calc_horizontal_sliding(
    soil_profile: SoilProfile,
    foundation: Foundation,
    loads: Loads,
    foundation_pressure: float,
) -> HorizontalSlidingResult:
    """Calculates horizontal sliding stability based on foundation and soil parameters.

    Args:
        soil_profile: The soil profile containing soil layers and properties
        foundation: The foundation parameters including dimensions and friction coefficient
        loads: The loads acting on the foundation
        foundation_pressure: The pressure exerted by the foundation on the soil

    Returns:
        HorizontalSlidingResult: A result containing the calculated values and safety checks

    Raises:
        ValidationError: If validation fails
    """
    validate_input(soil_profile, foundation, loads, foundation_pressure)

    if foundation.foundation_depth is None:
        raise ValueError("Foundation depth must be set")
    if foundation.foundation_width is None:
        raise ValueError("Foundation width must be set")
    if foundation.foundation_length is None:
        raise ValueError("Foundation length must be set")
    if loads.horizontal_load_x is None:
        raise ValueError("Horizontal load x must be set")
    if loads.horizontal_load_y is None:
        raise ValueError("Horizontal load y must be set")
    if foundation.surface_friction_coefficient is None:
        raise ValueError("Surface friction coefficient must be set")
    if soil_profile.ground_water_level is None:
        raise ValueError("Ground water level must be set")

    df = foundation.foundation_depth
    b = foundation.foundation_width
    l = foundation.foundation_length

    vx = loads.horizontal_load_x
    vy = loads.horizontal_load_y
    surface_friction = foundation.surface_friction_coefficient

    ptv = foundation_pressure * b * l

    cohesion, phi, unit_weight = get_soil_params(soil_profile, df)

    kp = math.tan(math.radians(45.0 + phi / 2.0)) ** 2

    if soil_profile.ground_water_level > df:
        rth = ptv * surface_friction / 1.1
    else:
        rth = l * b * cohesion / 1.1

    rpk_x = b * 0.5 * df**2 * unit_weight * kp
    rpk_y = l * 0.5 * df**2 * unit_weight * kp

    rpt_x = rpk_x / 1.4
    rpt_y = rpk_y / 1.4

    sum_x = rth + 0.3 * rpt_x
    sum_y = rth + 0.3 * rpt_y

    return HorizontalSlidingResult(
        rth=rth,
        ptv=ptv,
        rpk_x=rpk_x,
        rpk_y=rpk_y,
        rpt_x=rpt_x,
        rpt_y=rpt_y,
        sum_x=sum_x,
        sum_y=sum_y,
        is_safe_x=vx <= sum_x,
        is_safe_y=vy <= sum_y,
        ac=l * b,
        vth_x=vx,
        vth_y=vy,
    )
