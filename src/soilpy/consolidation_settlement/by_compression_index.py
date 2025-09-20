"""Consolidation settlement calculation using compression index method."""

import math
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
    soil_profile.validate(
        [
            "thickness",
            "compression_index",
            "recompression_index",
            "void_ratio",
            "preconsolidation_pressure",
        ]
    )
    foundation.validate(["foundation_depth"])
    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )


def calc_single_layer_settlement(
    h: float,
    cc: float,
    cr: float,
    e0: float,
    gp: float,
    g0: float,
    delta_stress: float,
) -> float:
    """Calculates consolidation settlement using Cc-Cr method (logarithmic compression).

    Args:
        h: Thickness of the compressible layer [m]
        cc: Compression Index (Cc)
        cr: Recompression Index (Cr)
        e0: Initial Void Ratio (e₀)
        gp: Preconsolidation Pressure [kPa]
        g0: Initial Effective Stress [kPa]
        delta_stress: Stress increase due to foundation [kPa]

    Returns:
        Settlement [cm]
    """
    if g0 >= gp:
        settlement = cc * (h / (1.0 + e0)) * math.log10((delta_stress + g0) / g0)
    elif (delta_stress + g0) <= gp:
        settlement = cr * (h / (1.0 + e0)) * math.log10((delta_stress + g0) / g0)
    else:
        settlement = cr * (h / (1.0 + e0)) * math.log10(gp / g0) + cc * (
            h / (1.0 + e0)
        ) * math.log10((delta_stress + g0) / gp)

    return max(settlement, 0.0) * 100.0  # Convert to cm


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
        delta_stress = calc_delta_stress(q_net, width, length, center)
        g0 = soil_profile.calc_effective_stress(center)

        if layer.compression_index is None:
            raise ValueError("Compression index must be set")
        if layer.recompression_index is None:
            raise ValueError("Recompression index must be set")
        if layer.void_ratio is None:
            raise ValueError("Void ratio must be set")
        if layer.preconsolidation_pressure is None:
            raise ValueError("Preconsolidation pressure must be set")

        cc = layer.compression_index
        cr = layer.recompression_index
        e0 = layer.void_ratio
        gp = layer.preconsolidation_pressure

        settlement = calc_single_layer_settlement(thickness, cc, cr, e0, gp, g0, delta_stress)
        settlements.append(settlement)

    return SettlementResult(
        settlement_per_layer=settlements.copy(),
        total_settlement=sum(settlements),
        qnet=q_net,
    )
