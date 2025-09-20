"""Helper functions for liquefaction analysis in SoilPy."""

import math


def calc_rd(depth: float) -> float:
    """Calculates stress reduction factor (rd) based on depth.

    Args:
        depth: Depth in meters

    Returns:
        rd: Stress reduction coefficient
    """
    if depth <= 9.15:
        return 1.0 - 0.00765 * depth
    elif 9.15 < depth < 23.0:
        return 1.174 - 0.0267 * depth
    elif 23.0 <= depth < 30.0:
        return 0.744 - 0.008 * depth
    else:
        return 0.5


def calc_csr(pga: float, normal_stress: float, rd: float) -> float:
    """Calculates cyclic stress ratio (CSR) based on PGA, normal stress, and rd.

    Args:
        pga: Peak Ground Acceleration
        normal_stress: Normal stress in ton/m²
        rd: Stress reduction coefficient

    Returns:
        CSR: Cyclic stress ratio
    """
    return 0.65 * pga * normal_stress * rd


def calc_msf(mw: float) -> float:
    """Calculates magnitude scaling factor (MSF) based on moment magnitude.

    Args:
        mw: Moment magnitude

    Returns:
        msf: Magnitude scaling factor
    """
    return 10.0**2.24 / mw**2.56


def calc_cn(effective_stress: float) -> float:
    """Calculates Cn correction factor based on effective stress.

    Args:
        effective_stress: Effective stress in ton/m²

    Returns:
        cn: Cn correction factor
    """
    cn = 1.16 * (1.0 / effective_stress) ** 0.5
    return min(cn, 1.7)


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
