"""Consolidation settlement calculation using coefficient of volume compressibility (mv)."""

from typing import List

from soilpy.consolidation_settlement.helper_functions import (
    calc_delta_stress,
    get_center_and_thickness,
)
from soilpy.consolidation_settlement.model import SettlementResult
from soilpy.models import Foundation, SoilProfile
from soilpy.validation import ValidationError, validate_field


def validate_input(
    soil_profile: SoilProfile,
    foundation: Foundation,
    foundation_pressure: float,
) -> None:
    """Validates the input parameters for the consolidation settlement calculation.

    Args:
        soil_profile: The soil profile containing the layers
        foundation: The foundation parameters
        foundation_pressure: The foundation pressure (q) [t/m²]

    Raises:
        ValidationError: If validation fails
    """
    soil_profile.validate(["thickness", "mv"])
    foundation.validate(["foundation_depth"])
    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )


def calc_single_layer_settlement(mv: float, h: float, delta_stress: float) -> float:
    """Calculates settlement of a single layer using coefficient of volume compressibility.

    Args:
        mv: Coefficient of volume compressibility [m²/t]
        h: Thickness of the layer [m]
        delta_stress: Change in effective stress [t/m²]

    Returns:
        Settlement of the layer [cm]
    """
    return mv * h * delta_stress * 100.0


def calc_settlement(
    soil_profile: SoilProfile,
    foundation: Foundation,
    foundation_pressure: float,
) -> SettlementResult:
    """Calculates the consolidation settlement of a foundation based on the soil profile and foundation parameters.

    Args:
        soil_profile: The soil profile containing the layers
        foundation: The foundation parameters
        foundation_pressure: The foundation pressure (q) [t/m²]

    Returns:
        SettlementResult: A result containing settlements for each layer

    Raises:
        ValidationError: If validation fails
    """
    validate_input(soil_profile, foundation, foundation_pressure)
    soil_profile.calc_layer_depths()

    settlements: List[float] = []

    if foundation.foundation_depth is None:
        raise ValueError("Foundation depth must be set")
    if foundation.foundation_width is None:
        raise ValueError("Foundation width must be set")
    if foundation.foundation_length is None:
        raise ValueError("Foundation length must be set")
    if soil_profile.ground_water_level is None:
        raise ValueError("Ground water level must be set")

    df = foundation.foundation_depth
    width = foundation.foundation_width
    length = foundation.foundation_length
    q_net = foundation_pressure - soil_profile.calc_normal_stress(df)
    gwt = soil_profile.ground_water_level

    for i in range(len(soil_profile.layers)):
        if soil_profile.get_layer_index(gwt) > i or soil_profile.get_layer_index(df) > i:
            settlements.append(0.0)
            continue

        layer = soil_profile.layers[i]
        center, thickness = get_center_and_thickness(soil_profile, df, i)

        if layer.mv is None:
            raise ValueError("Coefficient of volume compressibility (mv) must be set")

        mv = layer.mv
        delta_stress = calc_delta_stress(q_net, width, length, center)
        settlement = calc_single_layer_settlement(mv, thickness, delta_stress)
        settlements.append(settlement)

    return SettlementResult(
        settlement_per_layer=settlements.copy(),
        total_settlement=sum(settlements),
        qnet=q_net,
    )
