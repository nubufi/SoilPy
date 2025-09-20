"""Tezcan & Ozdemir bearing capacity calculations for SoilPy."""

from dataclasses import dataclass
from typing import Optional

from soilpy.models import Foundation, Masw, SoilProfile
from soilpy.validation import ValidationError


@dataclass
class Output:
    """Represents the bearing capacity result for a given soil and foundation setup."""

    vs: float  # Shear wave velocity (Vs) in m/s
    unit_weight: float  # Unit weight of the soil in t/m³
    qmax: float  # The pressure exerted by the foundation in ton/m2
    allowable_bearing_capacity: float  # Allowable bearing capacity in ton/m2
    is_safe: bool  # Indicates whether the bearing capacity is safe
    safety_factor: float  # Safety factor used in the design


def validate_input(
    masw: Masw,
    soil_profile: SoilProfile,
    foundation: Foundation,
) -> None:
    """Validates the input data for Tezcan & Ozdemir bearing capacity calculations.

    Args:
        masw: The MASW data
        soil_profile: The soil profile data
        foundation: The foundation data

    Raises:
        ValidationError: If validation fails
    """
    masw.validate(["thickness", "vs"])
    soil_profile.validate(["thickness", "dry_unit_weight", "saturated_unit_weight"])
    foundation.validate(["foundation_depth"])


def get_unit_weight(df: float, soil_profile: SoilProfile) -> float:
    """Retrieves the soil parameters (unit weight) at a given depth.

    Args:
        df: Depth at which to retrieve the soil parameters
        soil_profile: The soil profile containing the layers and their properties

    Returns:
        The unit weight of the soil at the given depth
    """
    layer = soil_profile.get_layer_at_depth(df)

    if soil_profile.ground_water_level is None:
        raise ValueError("Ground water level must be set")

    gwt = soil_profile.ground_water_level

    if layer.dry_unit_weight is None:
        raise ValueError("Dry unit weight must be set")

    unit_weight = layer.dry_unit_weight

    if gwt <= df:
        if layer.saturated_unit_weight is None:
            raise ValueError("Saturated unit weight must be set")
        unit_weight = layer.saturated_unit_weight

    return unit_weight


def calc_bearing_capacity(
    soil_profile: SoilProfile,
    masw: Masw,
    foundation: Foundation,
    foundation_pressure: float,
) -> Output:
    """Calculates the ultimate bearing capacity of a foundation based on
    shear wave velocity (Vs), soil unit weight, and empirical relationships.
    It uses the method proposed by Tezcan and Ozdemir (2007).

    Args:
        soil_profile: A struct containing the soil layers and properties
        masw: A struct representing the MASW data
        foundation: A struct representing the foundation geometry (e.g., depth)
        foundation_pressure: The pressure applied by the foundation in t/m2

    Returns:
        Output: The calculated bearing capacity result

    Raises:
        ValidationError: If validation fails
    """
    # Validate the input parameters
    validate_input(masw, soil_profile, foundation)

    if foundation.foundation_depth is None:
        raise ValueError("Foundation depth must be set")

    df = foundation.foundation_depth
    masw_exp = masw.get_idealized_exp("idealized")

    masw_layer = masw_exp.get_layer_at_depth(df)
    if masw_layer.vs is None:
        raise ValueError("Shear wave velocity must be set")

    vs = masw_layer.vs
    unit_weight = get_unit_weight(df, soil_profile)

    if vs < 750.0:
        safety_factor = 4.0
        bearing_capacity = 0.025 * unit_weight * vs
    elif vs < 4000.0:
        safety_factor = 4.6 - vs * 8.0e-4
        bearing_capacity = 0.1 * unit_weight * vs / safety_factor
    else:
        safety_factor = 1.4
        bearing_capacity = 0.071 * unit_weight * vs

    return Output(
        vs=vs,
        unit_weight=unit_weight,
        allowable_bearing_capacity=bearing_capacity,
        is_safe=bearing_capacity >= foundation_pressure,
        safety_factor=safety_factor,
        qmax=foundation_pressure,
    )
