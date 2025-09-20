"""Liquefaction analysis using Andrus & Stokoe method based on Vs data for SoilPy."""

import math
from typing import List

from soilpy.helper import interp1d
from soilpy.liquefaction.helper_functions import calc_csr, calc_msf, calc_rd
from soilpy.liquefaction.models import (
    CommonLiquefactionLayerResult,
    VSLiquefactionLayerResult,
    VSLiquefactionResult,
)
from soilpy.models import Masw, SoilProfile
from soilpy.validation import ValidationError


def validate_input(masw: Masw, soil_profile: SoilProfile) -> None:
    """Validates the input data for liquefaction calculations.

    Args:
        masw: The MASW data
        soil_profile: The soil profile data

    Raises:
        ValidationError: If validation fails
    """
    masw.validate(["thickness", "vs"])
    soil_profile.validate(
        [
            "thickness",
            "dry_unit_weight",
            "saturated_unit_weight",
            "plasticity_index",
            "fine_content",
        ]
    )


def calc_vs1c(fine_content: float) -> float:
    """Calculates Vs1c based on fine content.

    Args:
        fine_content: Fine content in percentage

    Returns:
        vs1c: Vs1c value
    """
    if fine_content <= 5.0:
        return 215.0
    elif 5.0 < fine_content <= 35.0:
        return 215.0 - 0.5 * (fine_content - 5.0)
    else:
        return 200.0


def calc_crr75(vs1: float, vs1c: float, effective_stress: float) -> float:
    """Calculates cyclic resistance ratio (CRR) based on N1_60 and effective stress.

    Args:
        vs1: Vs1 value
        vs1c: Vs1c value
        effective_stress: Effective stress in ton/m²

    Returns:
        crr: Cyclic resistance ratio
    """
    return ((0.03 * (vs1 / 100.0) ** 2.0) + 0.09 / (vs1c - vs1) - 0.09 / vs1c) * effective_stress


def calc_cn(effective_stress: float) -> float:
    """Calculates Cn correction factor based on effective stress.

    Args:
        effective_stress: Effective stress in ton/m²

    Returns:
        cn: Cn correction factor
    """
    cn = 1.16 * (1.0 / effective_stress) ** 0.5
    return min(cn, 1.7)


def calc_settlement(fs: float, layer_thickness: float, vs1: float) -> float:
    """Calculates settlement due to liquefaction for a single layer.

    Args:
        fs: Factor of Safety
        layer_thickness: Thickness of the layer (m)
        vs1: Vs1c value

    Returns:
        Settlement in cm
    """
    dr = 17.974 * (vs1 / 100.0) ** 1.976

    a0 = 0.3773
    a1 = -0.0337
    a2 = 1.5672
    a3 = -0.1833
    b0 = 28.45
    b1 = -9.3372
    b2 = 0.7975

    dr_list = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
    q_list = [33.0, 45.0, 60.0, 80.0, 110.0, 147.0, 200.0]

    q = interp1d(dr_list, q_list, dr)

    if fs > 2.0:
        settlement = 0.0
    elif fs < 2.0 and fs > (2.0 - 1.0 / (a2 + a3 * math.log(q))):
        s1 = (a0 + a1 * math.log(q)) / ((1.0 / (2.0 - fs)) - (a2 + a3 * math.log(q)))
        s2 = b0 + b1 * math.log(q) + b2 * (math.log(q) ** 2)
        settlement = min(s1, s2)
    else:
        settlement = b0 + b1 * math.log(q) + b2 * (math.log(q) ** 2)

    return settlement * layer_thickness


def calc_liquefacion(
    soil_profile: SoilProfile, masw: Masw, pga: float, mw: float
) -> VSLiquefactionResult:
    """Calculates liquefaction potential for a soil profile using SPT data.

    Args:
        soil_profile: Soil profile data
        masw: MASW data
        pga: Peak Ground Acceleration
        mw: Moment magnitude

    Returns:
        VSLiquefactionResult: Result of liquefaction analysis

    Raises:
        ValidationError: If validation fails
    """
    validate_input(masw, soil_profile)
    soil_profile.calc_layer_depths()

    masw_exp = masw.get_idealized_exp("idealized")
    masw_exp.calc_depths()

    msf = calc_msf(mw)
    layer_results: List[CommonLiquefactionLayerResult] = []
    vs_layers: List[VSLiquefactionLayerResult] = []

    for layer in soil_profile.layers:
        thickness = layer.thickness
        depth = layer.depth
        rd = calc_rd(depth)
        effective_stress = soil_profile.calc_effective_stress(depth)
        normal_stress = soil_profile.calc_normal_stress(depth)
        soil_layer = soil_profile.get_layer_at_depth(depth)
        plasticity_index = soil_layer.plasticity_index
        masw_layer = masw_exp.get_layer_at_depth(depth)
        vs = masw_layer.vs
        cn = calc_cn(effective_stress)
        vs1 = vs * cn
        vs1c = calc_vs1c(soil_layer.fine_content)

        conditions = [
            soil_profile.ground_water_level >= depth,
            plasticity_index >= 12.0,
            vs1 >= vs1c,
        ]

        if any(conditions):
            layer_result = CommonLiquefactionLayerResult(
                soil_layer=soil_layer,
                depth=depth,
                normal_stress=normal_stress,
                effective_stress=effective_stress,
                rd=rd,
            )
            layer_results.append(layer_result)
            continue

        csr = calc_csr(pga, normal_stress, rd)
        crr75 = calc_crr75(vs1, vs1c, effective_stress)
        crr = msf * crr75
        safety_factor = crr / csr
        settlement = calc_settlement(safety_factor, thickness, vs1)

        vs_layer_result = VSLiquefactionLayerResult(
            vs=vs,
            vs1=vs1,
            vs1c=vs1c,
            cn=cn,
        )
        vs_layers.append(vs_layer_result)

        layer_result = CommonLiquefactionLayerResult(
            soil_layer=soil_layer,
            depth=depth,
            normal_stress=normal_stress,
            effective_stress=effective_stress,
            crr=crr,
            crr75=crr75,
            csr=csr,
            safety_factor=safety_factor,
            is_safe=safety_factor > 1.1,
            settlement=settlement,
            rd=rd,
        )
        layer_results.append(layer_result)

    total_settlement = sum(layer.settlement for layer in layer_results)

    return VSLiquefactionResult(
        layers=layer_results,
        vs_layers=vs_layers,
        total_settlement=total_settlement,
        msf=msf,
    )
