"""Liquefaction analysis using Seed & Idriss method based on SPT data for SoilPy."""

import math
from typing import List

from soilpy.helper import interp1d
from soilpy.liquefaction.helper_functions import calc_csr, calc_msf, calc_rd
from soilpy.liquefaction.models import (
    CommonLiquefactionLayerResult,
    SptLiquefactionResult,
)
from soilpy.models import SPT, SoilProfile, SPTExp
from soilpy.validation import ValidationError


def validate_input(soil_profile: SoilProfile, spt: SPT) -> None:
    """Validates the soil profile and SPT data.

    Args:
        soil_profile: Soil profile data
        spt: SPT data

    Raises:
        ValidationError: If validation fails
    """
    spt.validate(["n", "depth"])
    soil_profile.validate(
        [
            "thickness",
            "dry_unit_weight",
            "saturated_unit_weight",
            "plasticity_index",
            "fine_content",
        ]
    )


def prepare_spt_exp(spt: SPT, soil_profile: SoilProfile) -> SPTExp:
    """Prepares the SPT experiment data.

    Args:
        spt: SPT data
        soil_profile: Soil profile data

    Returns:
        SPTExp: Prepared SPT experiment data
    """
    cs = spt.sampler_correction_factor
    cb = spt.diameter_correction_factor
    ce = spt.energy_correction_factor

    spt_exp = spt.get_idealized_exp("idealized")
    spt_exp.apply_corrections(soil_profile, cs, cb, ce)
    spt_exp.calc_thicknesses()

    return spt_exp


def calc_crr75(n1_60_f: int, effective_stress: float) -> float:
    """Calculates cyclic resistance ratio (CRR) based on N1_60 and effective stress.

    Args:
        n1_60_f: N1_60f value
        effective_stress: Effective stress in ton/m²

    Returns:
        crr: Cyclic resistance ratio
    """
    n1_60_f_float = float(n1_60_f)
    return (
        (1.0 / (34.0 - n1_60_f_float))
        + (n1_60_f_float / 135.0)
        + (50.0 / ((10.0 * n1_60_f_float + 45.0) ** 2))
        - (1.0 / 200.0)
    ) * effective_stress


def calc_settlement(fs: float, layer_thickness: float, n60: int) -> float:
    """Calculates settlement due to liquefaction for a single layer.

    Args:
        fs: Factor of Safety
        layer_thickness: Thickness of the layer (m)
        n60: Corrected N60 value

    Returns:
        Settlement in cm
    """
    n90 = max(3.0, min(30.0, float(n60) * 6.0 / 9.0))

    a0 = 0.3773
    a1 = -0.0337
    a2 = 1.5672
    a3 = -0.1833
    b0 = 28.45
    b1 = -9.3372
    b2 = 0.7975

    n90_list = [3.0, 6.0, 10.0, 14.0, 25.0, 30.0]
    q_list = [33.0, 45.0, 60.0, 80.0, 147.0, 200.0]

    q = interp1d(n90_list, q_list, n90)

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
    soil_profile: SoilProfile, spt: SPT, pga: float, mw: float
) -> SptLiquefactionResult:
    """Calculates liquefaction potential for a soil profile using SPT data.

    Args:
        soil_profile: Soil profile data
        spt: SPT data
        pga: Peak Ground Acceleration
        mw: Moment magnitude

    Returns:
        SptLiquefactionResult: Result of liquefaction analysis

    Raises:
        ValidationError: If validation fails
    """
    validate_input(soil_profile, spt)
    spt_exp = prepare_spt_exp(spt, soil_profile)
    msf = calc_msf(mw)
    layer_results: List[CommonLiquefactionLayerResult] = []

    for blow in spt_exp.blows:
        thickness = blow.thickness
        depth = blow.depth
        rd = calc_rd(depth)
        n60 = blow.n60.to_i32()
        n1_60 = blow.n1_60.to_i32()
        n1_60_f = blow.n1_60f.to_i32()
        effective_stress = soil_profile.calc_effective_stress(depth)
        normal_stress = soil_profile.calc_normal_stress(depth)
        soil_layer = soil_profile.get_layer_at_depth(depth)
        plasticity_index = soil_layer.plasticity_index

        conditions = [
            soil_profile.ground_water_level >= depth,
            plasticity_index >= 12.0,
            n1_60 >= 30,
            n1_60_f >= 34,
        ]

        if any(conditions):
            layer_result = CommonLiquefactionLayerResult(
                depth=depth,
                normal_stress=normal_stress,
                effective_stress=effective_stress,
                rd=rd,
            )
            layer_results.append(layer_result)
            continue

        csr = calc_csr(pga, normal_stress, rd)
        crr75 = calc_crr75(n1_60_f, effective_stress)
        crr = msf * crr75
        safety_factor = crr / csr
        settlement = calc_settlement(safety_factor, thickness, n60)

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

    return SptLiquefactionResult(
        layers=layer_results,
        spt_exp=spt_exp,
        total_settlement=total_settlement,
        msf=msf,
    )
