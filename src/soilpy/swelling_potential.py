"""Swelling potential calculations for SoilPy."""

from typing import List

from pydantic import BaseModel

from soilpy.models import Foundation, SoilProfile
from soilpy.validation import ValidationError, validate_field


class SwellingPotentialData(BaseModel):
    """Represents the swelling potential data for a soil layer."""

    layer_center: float  # The center depth of the layer in meters
    effective_stress: float  # The effective stress at the center of the layer in ton/m2
    delta_stress: float  # The change in stress due to the foundation load in ton/m2
    swelling_pressure: float  # The calculated swelling pressure for the layer in ton/m2
    is_safe: bool  # Indicates whether the swelling pressure is safe compared to the effective stress


class SwellingPotentialResult(BaseModel):
    """Represents the result of the swelling potential calculation."""

    data: List[SwellingPotentialData]  # Swelling potential data for each layer
    net_foundation_pressure: float  # The net foundation pressure in ton/m2


def validate_input(
    soil_profile: SoilProfile,
    foundation: Foundation,
    foundation_pressure: float,
) -> None:
    """Validates the input data for swelling potential calculations.

    Args:
        soil_profile: The soil profile data
        foundation: The foundation data
        foundation_pressure: The foundation pressure (q) [t/m²]

    Raises:
        ValidationError: If validation fails
    """
    soil_profile.validate(
        [
            "thickness",
            "dry_unit_weight",
            "saturated_unit_weight",
            "water_content",
            "liquid_limit",
            "plastic_limit",
        ]
    )
    foundation.validate(["foundation_depth", "foundation_width", "foundation_length"])

    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )


def calc_swelling_potential(
    soil_profile: SoilProfile,
    foundation: Foundation,
    foundation_pressure: float,
) -> SwellingPotentialResult:
    """Calculates the swelling potential of a soil profile based on the foundation parameters using
    Kayabalu & Yaldız (2014) method.

    Args:
        soil_profile: The soil profile containing the layers of soil
        foundation: The foundation parameters including depth, width, and length
        foundation_pressure: The foundation pressure applied to the soil in ton/m2

    Returns:
        SwellingPotentialResult: A result containing the swelling potential data for each layer and the net foundation pressure

    Raises:
        ValidationError: If validation fails
    """
    validate_input(soil_profile, foundation, foundation_pressure)
    soil_profile.calc_layer_depths()

    if foundation.foundation_depth is None:
        raise ValueError("Foundation depth must be set")
    if foundation.foundation_width is None:
        raise ValueError("Foundation width must be set")
    if foundation.foundation_length is None:
        raise ValueError("Foundation length must be set")

    df = foundation.foundation_depth
    width = foundation.foundation_width
    length = foundation.foundation_length

    net_foundation_pressure = foundation_pressure - soil_profile.calc_normal_stress(df)
    vertical_load = net_foundation_pressure * width * length

    data: List[SwellingPotentialData] = []

    for layer in soil_profile.layers:
        if layer.center is None:
            raise ValueError("Layer center must be set")

        z = layer.center
        effective_stress = 0.0
        delta_stress = 0.0

        if z >= df:
            effective_stress = soil_profile.calc_effective_stress(z)
            delta_stress = vertical_load / ((width + z - df) * (length + z - df))

        if layer.plastic_limit is not None:
            if layer.water_content is None:
                raise ValueError("Water content must be set")
            if layer.liquid_limit is None:
                raise ValueError("Liquid limit must be set")
            if layer.dry_unit_weight is None:
                raise ValueError("Dry unit weight must be set")

            water_content = layer.water_content
            liquid_limit = layer.liquid_limit
            dry_unit_weight = layer.dry_unit_weight
            plastic_limit = layer.plastic_limit

            swelling_pressure = (
                -3.08 * water_content
                + 102.5 * dry_unit_weight
                + 0.635 * liquid_limit
                + 4.24 * plastic_limit
                - 220.8
            )
        else:
            swelling_pressure = 0.0

        is_safe = swelling_pressure <= (effective_stress + delta_stress)

        data.append(
            SwellingPotentialData(
                layer_center=layer.center,
                effective_stress=effective_stress,
                delta_stress=delta_stress,
                swelling_pressure=swelling_pressure,
                is_safe=is_safe,
            )
        )

    return SwellingPotentialResult(
        data=data,
        net_foundation_pressure=net_foundation_pressure,
    )
