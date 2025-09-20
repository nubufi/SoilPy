"""Boussinesq elastic settlement calculations for SoilPy."""

import math
from typing import List

from soilpy.consolidation_settlement.model import SettlementResult
from soilpy.elastic_settlement.reduction_factors import interpolate_if
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
    soil_profile.validate(
        [
            "thickness",
            "dry_unit_weight",
            "saturated_unit_weight",
            "elastic_modulus",
            "poissons_ratio",
        ]
    )
    foundation.validate(["foundation_depth", "foundation_width", "foundation_length"])

    validate_field(
        "foundation_pressure",
        foundation_pressure,
        0.0,
        error_code_prefix="loads",
    )


def calc_ip(h: float, b: float, l: float, u: float) -> float:
    """Calculates the influence factor (Ip) for settlement under a rectangular foundation.

    Args:
        h: Depth of the layer (H) [m]
        b: Width of foundation (B) [m]
        l: Length of foundation (L) [m]
        u: Poisson's ratio of the soil (ν) [-]

    Returns:
        Ip: Influence factor (dimensionless)

    Reference:
        Bowles, J.E. (1996). *Foundation Analysis and Design*, 5th Ed.
    """
    m = l / b
    n = 2.0 * h / b

    m2 = m * m
    n2 = n * n

    a0 = m * math.log(
        (1.0 + math.sqrt(1.0 + m2)) * math.sqrt(m2 + n2) / (m * (1.0 + math.sqrt(1.0 + m2 + n2)))
    )
    a1 = math.log((m + math.sqrt(1.0 + m2)) * math.sqrt(1.0 + n2) / (m + math.sqrt(1.0 + m2 + n2)))
    if n == 0.0 or math.sqrt(1.0 + m2 + n2) == 0.0:
        a2 = 0.0
    else:
        a2 = m / (n * math.sqrt(1.0 + m2 + n2))

    f1 = (a0 + a1) / math.pi
    f2 = 0.5 * (n / math.pi) * math.atan(a2)

    return f1 + ((1.0 - 2.0 * u) / (1.0 - u)) * f2


def single_layer_settlement(
    h: float, u: float, e: float, l: float, b: float, df: float, q_net: float
) -> float:
    """Calculates the settlement (S) of a single soil layer under a rectangular foundation.

    Args:
        h: Thickness of the soil layer (H) [m]
        u: Poisson's ratio of the soil (ν) [-]
        e: Elastic Modulus of the soil (E) [kPa]
        l: Length of the foundation (L) [m]
        b: Width of the foundation (B) [m]
        df: Depth of foundation (Df) [m]
        q_net: Net foundation pressure (qNet) [t/m²]

    Returns:
        S: Settlement in centimeters [cm]

    Formula:
        S = 100 * qNet * 4 * B * If * Ip * (1 - u²) * 0.5 / E

    Reference: Bowles, J.E. (1996)
    """
    lb = l / b
    db = df / b
    ip = calc_ip(h, b, l, u)
    if_value = interpolate_if(u, db, lb)

    return 100.0 * q_net * 4.0 * b * if_value * ip * (1.0 - u**2) * 0.5 / e


def calc_elastic_settlement(
    soil_profile: SoilProfile,
    foundation: Foundation,
    foundation_pressure: float,
) -> SettlementResult:
    """Calculates the elastic settlement of a foundation based on the soil profile and foundation parameters.

    Args:
        soil_profile: The soil profile containing the layers of soil
        foundation: The foundation parameters
        foundation_pressure: The foundation pressure (q) [t/m²]

    Returns:
        SettlementResult: A result containing settlements for each layer

    Raises:
        ValidationError: If validation fails

    Reference: Bowles, J.E. (1996)
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

    df = foundation.foundation_depth
    width = foundation.foundation_width
    length = foundation.foundation_length

    q_net = foundation_pressure - soil_profile.calc_normal_stress(df)
    df_index = soil_profile.get_layer_index(df)

    for i in range(len(soil_profile.layers)):
        layer = soil_profile.layers[i]

        if layer.depth is None:
            raise ValueError("Layer depth must be set")
        if layer.poissons_ratio is None:
            raise ValueError("Poisson's ratio must be set")
        if layer.elastic_modulus is None:
            raise ValueError("Elastic modulus must be set")

        h = layer.depth - df
        u = layer.poissons_ratio
        e = layer.elastic_modulus

        if i < df_index:
            settlements.append(0.0)
        else:
            settlement_all = single_layer_settlement(h, u, e, length, width, df, q_net)
            if i == 0:
                settlements.append(max(settlement_all, 0.0))
            else:
                if soil_profile.layers[i - 1].depth is None:
                    raise ValueError("Previous layer depth must be set")
                h0 = soil_profile.layers[i - 1].depth - df
                settlement_prevlayer = single_layer_settlement(h0, u, e, length, width, df, q_net)
                settlements.append(max(settlement_all - settlement_prevlayer, 0.0))

    return SettlementResult(
        settlement_per_layer=settlements.copy(),
        total_settlement=sum(settlements),
        qnet=q_net,
    )
