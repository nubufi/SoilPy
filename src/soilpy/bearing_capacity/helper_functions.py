"""Helper functions for bearing capacity calculations."""

import math

from ..enums import AnalysisTerm
from ..models import Foundation, SoilProfile
from .model import SoilParams


def compute_equivalent_unit_weights(
    profile: SoilProfile, depth_limit: float
) -> tuple[float, float]:
    """Computes the equivalent dry (γ1) and saturated (γ2) unit weights up to a specified depth_limit.

    Args:
        profile: Soil profile
        depth_limit: Depth limit for calculation

    Returns:
        Tuple of (γ1, γ2), both rounded to 3 decimal places
    """
    prev_depth = 0.0
    gamma_dry_sum = 0.0
    gamma_saturated_sum = 0.0

    depth_index = profile.get_layer_index(depth_limit)

    for i, layer in enumerate(profile.layers[: depth_index + 1]):
        if layer.thickness is None:
            raise ValueError("Layer thickness must be set")

        thickness = (
            depth_limit - prev_depth
            if layer.depth and layer.depth >= depth_limit
            else layer.thickness
        )

        if layer.dry_unit_weight is None or layer.saturated_unit_weight is None:
            raise ValueError("Unit weights must be set")

        gamma_dry_sum += layer.dry_unit_weight * thickness
        gamma_saturated_sum += layer.saturated_unit_weight * thickness

        if layer.depth is not None:
            prev_depth = layer.depth

    total_depth = min(depth_limit, profile.layers[-1].depth or 0.0)

    gamma_dry = round(gamma_dry_sum / total_depth * 1000.0) / 1000.0
    gamma_saturated = round(gamma_saturated_sum / total_depth * 1000.0) / 1000.0

    return (gamma_dry, gamma_saturated)


def calc_effective_surcharge(
    soil_profile: SoilProfile, foundation_data: Foundation, term: AnalysisTerm
) -> float:
    """Calculates the effective surcharge (overburden pressure) at the foundation level.

    Args:
        soil_profile: SoilProfile with unit weights and groundwater depth
        foundation_data: Foundation data containing foundation depth and width
        term: Load duration term (Short or Long)

    Returns:
        Effective vertical stress at foundation level in kPa
    """
    if foundation_data.foundation_depth is None or foundation_data.effective_width is None:
        raise ValueError("Foundation depth and effective width must be set")

    df = foundation_data.foundation_depth
    width = foundation_data.effective_width

    gamma_dry, gamma_saturated = compute_equivalent_unit_weights(soil_profile, df)
    gamma_effective = gamma_saturated - 0.981  # γ_w assumed as 0.981 tf/m³ (≈ 9.81 kN/m³)

    if soil_profile.ground_water_level is None:
        raise ValueError("Ground water level must be set")

    gwt = soil_profile.ground_water_level if term == AnalysisTerm.SHORT else df + width

    if gwt <= df:
        return gamma_dry * gwt + gamma_effective * (df - gwt)
    else:
        return gamma_dry * df


def calc_effective_unit_weight(
    soil_profile: SoilProfile, foundation: Foundation, term: AnalysisTerm
) -> float:
    """Calculates the effective unit weight between the surface and Df + B.

    Args:
        soil_profile: The soil profile with layers and water level
        foundation: The foundation depth and width
        term: Short-term or long-term condition

    Returns:
        Effective unit weight (γ') in kN/m³
    """
    if foundation.foundation_depth is None or foundation.effective_width is None:
        raise ValueError("Foundation depth and effective width must be set")

    df = foundation.foundation_depth
    width = foundation.effective_width

    gamma_dry, gamma_saturated = compute_equivalent_unit_weights(soil_profile, df)
    gamma_effective = gamma_saturated - 0.981  # Subtract unit weight of water (kN/m³)

    if soil_profile.ground_water_level is None:
        raise ValueError("Ground water level must be set")

    gwt = soil_profile.ground_water_level if term == AnalysisTerm.SHORT else df + width

    if gwt <= df:
        # Entire zone is below groundwater
        return gamma_effective
    elif gwt < df + width:
        # Partially submerged zone
        d = df + width - gwt
        return gamma_effective + d * (gamma_dry - gamma_effective) / width
    else:
        # Entire zone is above groundwater
        return gamma_dry


def get_soil_params(
    soil_profile: SoilProfile, foundation: Foundation, term: AnalysisTerm
) -> SoilParams:
    """Retrieves the soil parameters (φ, c, γ') for a given foundation depth and term.

    Args:
        soil_profile: The soil profile with layers and water level
        foundation: The foundation depth and width
        term: Short-term or long-term condition

    Returns:
        SoilParams: Soil parameters (φ, c, γ') for the foundation depth and term
    """
    if foundation.foundation_depth is None:
        raise ValueError("Foundation depth must be set")

    depth = foundation.foundation_depth
    layer = soil_profile.get_layer_at_depth(depth)

    if term == AnalysisTerm.SHORT:
        if layer.phi_u is None or layer.cu is None:
            raise ValueError("Undrained parameters (phi_u, cu) must be set for short-term analysis")
        friction_angle = layer.phi_u
        cohesion = layer.cu
    else:  # LONG
        if layer.phi_prime is None or layer.c_prime is None:
            raise ValueError(
                "Effective parameters (phi_prime, c_prime) must be set for long-term analysis"
            )
        friction_angle = layer.phi_prime
        cohesion = layer.c_prime

    unit_weight = calc_effective_unit_weight(soil_profile, foundation, term)

    return SoilParams(friction_angle=friction_angle, cohesion=cohesion, unit_weight=unit_weight)
