"""Vesic bearing capacity calculations."""

import math

from ..enums import AnalysisTerm
from ..models import Foundation, Loads, SoilProfile
from ..validation import ValidationError
from .helper_functions import calc_effective_surcharge, get_soil_params
from .model import (
    BaseFactors,
    BearingCapacityFactors,
    BearingCapacityResult,
    DepthFactors,
    GroundFactors,
    InclinationFactors,
    ShapeFactors,
)


def validate_input(
    soil_profile: SoilProfile,
    foundation: Foundation,
    loading: Loads,
    term: AnalysisTerm,
) -> None:
    """Validates the input data for vesic's bearing capacity calculations.

    Args:
        soil_profile: The soil profile data
        foundation: The foundation data
        loading: The applied loads
        term: Short or long-term condition

    Raises:
        ValidationError: If validation fails
    """
    soil_profile.validate(["thickness", "dry_unit_weight", "saturated_unit_weight"])
    foundation.validate(["foundation_depth", "foundation_width", "foundation_length"])
    loading.validate(["vertical_load"])

    if soil_profile.layers[-1].depth is None or foundation.foundation_depth is None:
        raise ValueError("Layer depth and foundation depth must be set")

    if soil_profile.layers[-1].depth < foundation.foundation_depth:
        raise ValidationError(
            code="foundation.foundation_depth.smaller_than_soil_profile_depth",
            message="Foundation depth is smaller than the soil profile depth.",
        )

    for layer in soil_profile.layers:
        if term == AnalysisTerm.SHORT:
            layer.validate_fields(["cu", "phi_u"])

            if layer.cu is None or layer.phi_u is None:
                raise ValueError("Undrained parameters must be set")

            if layer.cu == 0.0 and layer.phi_u == 0.0:
                raise ValidationError(
                    code="soil_profile.layer.cu_or_phi_u_zero",
                    message="Either undrained shear strength (cu) or undrained friction angle (phi_u) must be greater than zero.",
                )
        else:  # LONG
            layer.validate_fields(["c_prime", "phi_prime"])

            if layer.c_prime is None or layer.phi_prime is None:
                raise ValueError("Effective parameters must be set")

            if layer.c_prime == 0.0 and layer.phi_prime == 0.0:
                raise ValidationError(
                    code="soil_profile.layer.c_prime_or_phi_prime_zero",
                    message="Either effective cohesion (c') or effective friction angle (phi') must be greater than zero.",
                )


def calc_bearing_capacity_factors(phi: float) -> BearingCapacityFactors:
    """Computes the bearing capacity factors Nc, Nq, and Ngamma based on the friction angle φ (degrees).

    Args:
        phi: Friction angle in degrees

    Returns:
        BearingCapacityFactors containing Nc, Nq, and Ng
    """
    phi_rad = math.radians(phi)

    tan_phi = math.tan(phi_rad)
    nq = math.exp(math.pi * tan_phi) * (math.tan(math.radians(45.0 + phi / 2.0))) ** 2

    nc = 5.14 if phi == 0.0 else (nq - 1.0) / tan_phi

    ng = 2.0 * (nq - 1.0) * tan_phi

    return BearingCapacityFactors(nc=nc, nq=nq, ng=ng)


def calc_shape_factors(
    foundation: Foundation, bearing_capacity_factors: BearingCapacityFactors, phi: float
) -> ShapeFactors:
    """Calculates shape factors (Sc, Sq, Sg) based on foundation geometry and bearing capacity factors.

    Args:
        foundation: Foundation data (width and length)
        bearing_capacity_factors: Nc, Nq, Ng
        phi: Friction angle in degrees

    Returns:
        ShapeFactors: shape coefficients for Sc, Sq, and Sg
    """
    if foundation.foundation_width is None or foundation.foundation_length is None:
        raise ValueError("Foundation width and length must be set")

    width = foundation.foundation_width
    length = foundation.foundation_length
    w_l = width / length

    nc = bearing_capacity_factors.nc
    nq = bearing_capacity_factors.nq

    sc = 0.2 * w_l if phi == 0.0 else 1.0 + w_l * (nq / nc)
    sq = 1.0 + w_l * math.sin(math.radians(phi))
    sg = max(1.0 - 0.4 * w_l, 0.6)

    return ShapeFactors(sc=sc, sq=sq, sg=sg)


def calc_base_factors(phi: float, foundation: Foundation) -> BaseFactors:
    """Calculates the base inclination factors (bc, bq, bg) for a given friction angle and foundation geometry.

    Args:
        phi: Internal friction angle in degrees
        foundation: Foundation struct with optional slope and foundation angles

    Returns:
        BaseFactors: The base inclination factors
    """
    slope_angle = foundation.slope_angle or 0.0
    base_tilt_angle = foundation.base_tilt_angle or 0.0

    slope_rad = math.radians(slope_angle)
    phi_rad = math.radians(phi)
    base_rad = math.radians(base_tilt_angle)

    bc = slope_rad / 5.14 if phi == 0.0 else 1.0 - 2.0 * slope_rad / (5.14 * math.tan(phi_rad))

    bq = (1.0 - base_rad * math.tan(phi_rad)) ** 2
    bg = bq

    return BaseFactors(bc=bc, bq=bq, bg=bg)


def calc_inclination_factors(
    phi: float,
    cohesion: float,
    bearing_capacity_factors: BearingCapacityFactors,
    foundation: Foundation,
    loading: Loads,
) -> InclinationFactors:
    """Calculates the inclination factors (ic, iq, ig) for a foundation under inclined loading.

    Args:
        phi: Internal friction angle of the soil in degrees
        cohesion: Cohesion of the soil in kPa
        bearing_capacity_factors: Reference to the BearingCapacityFactors struct
        foundation: Reference to the Foundation struct
        loading: Reference to the Loads struct

    Returns:
        InclinationFactors: Struct containing ic, iq, and ig
    """
    if foundation.foundation_width is None or foundation.foundation_length is None:
        raise ValueError("Foundation width and length must be set")

    w = foundation.foundation_width
    l = foundation.foundation_length

    if loading.vertical_load is None:
        raise ValueError("Vertical load must be set")

    vertical_load = loading.vertical_load
    hb = loading.horizontal_load_x or 0.0
    hl = loading.horizontal_load_y or 0.0
    hi = hb + hl

    if foundation.effective_width is None or foundation.effective_length is None:
        raise ValueError("Effective width and length must be set")

    effective_width = foundation.effective_width
    effective_length = foundation.effective_length
    area = effective_length * effective_width

    ca = cohesion * 0.75
    mb = (2.0 + w / l) / (1.0 + w / l)
    ml = (2.0 + l / w) / (1.0 + l / w)
    m = math.sqrt(mb**2 + ml**2)

    if hb == 0.0:
        m = ml
    elif hl == 0.0:
        m = mb

    nc = bearing_capacity_factors.nc
    nq = bearing_capacity_factors.nq

    iq = (
        1.0
        if phi == 0.0
        else (1.0 - hi / (vertical_load + area * ca / math.tan(math.radians(phi)))) ** m
    )

    ic = 1.0 - m * hi / (area * ca * nc) if phi == 0.0 else iq - (1.0 - iq) / (nq - 1.0)

    ig = (
        1.0
        if phi == 0.0
        else (1.0 - hi / (vertical_load + area * ca / math.tan(math.radians(phi)))) ** (m + 1.0)
    )

    return InclinationFactors(ic=ic, iq=iq, ig=ig)


def calc_depth_factors(foundation: Foundation, phi: float) -> DepthFactors:
    """Calculates the depth factors (dc, dq, dg) based on foundation geometry and soil friction angle.

    Args:
        foundation: Foundation data
        phi: Friction angle in degrees

    Returns:
        DepthFactors: dc, dq, dg coefficients
    """
    if foundation.foundation_depth is None or foundation.foundation_width is None:
        raise ValueError("Foundation depth and width must be set")

    df = foundation.foundation_depth
    w = foundation.foundation_width

    db = df / w if df / w <= 1.0 else math.atan(math.radians(df / w))

    phi_rad = math.radians(phi)
    tan_phi = math.tan(phi_rad)
    sin_phi = math.sin(phi_rad)

    dc = 0.4 * db if phi == 0.0 else 1.0 + 0.4 * db
    dq = 1.0 + 2.0 * tan_phi * (1.0 - sin_phi) ** 2 * db
    dg = 1.0

    return DepthFactors(dc=dc, dq=dq, dg=dg)


def calc_ground_factors(iq: float, slope_angle: float, phi: float) -> GroundFactors:
    """Calculates the ground modification factors (gc, gq, gg) due to slope.

    Args:
        iq: Load inclination factor (between 0 and 1)
        slope_angle: Slope angle in degrees
        phi: Soil friction angle in degrees

    Returns:
        GroundFactors with gc, gq, and gg
    """
    slope_rad = math.radians(slope_angle)
    phi_rad = math.radians(phi)

    gc = slope_rad / 5.14 if phi == 0.0 else iq - (1.0 - iq) / (5.14 * math.tan(phi_rad))

    tan_beta = math.tan(slope_rad)
    gq = (1.0 - tan_beta) ** 2
    gg = gq

    return GroundFactors(gc=gc, gq=gq, gg=gg)


def calc_bearing_capacity(
    soil_profile: SoilProfile,
    foundation: Foundation,
    loading: Loads,
    foundation_pressure: float,
    factor_of_safety: float,
    term: AnalysisTerm,
) -> BearingCapacityResult:
    """Calculates the ultimate and allowable bearing capacity of a foundation.

    Args:
        soil_profile: The soil profile data
        foundation: The foundation data
        loading: The applied loads
        foundation_pressure: The pressure on the foundation
        factor_of_safety: The safety factor to apply
        term: Short or long-term condition

    Returns:
        BearingCapacityResult with detailed components and safety check
    """
    # Validate input data
    validate_input(soil_profile, foundation, loading, term)
    soil_profile.calc_layer_depths()

    # Calculate effective foundation dimensions
    foundation.calc_effective_lengths(loading.moment_x or 0.0, loading.moment_y or 0.0)

    soil_params = get_soil_params(soil_profile, foundation, term)
    phi = soil_params.friction_angle
    cohesion = soil_params.cohesion
    effective_unit_weight = soil_params.unit_weight

    effective_surcharge = calc_effective_surcharge(soil_profile, foundation, term)

    bearing_capacity_factors = calc_bearing_capacity_factors(phi)
    shape_factors = calc_shape_factors(foundation, bearing_capacity_factors, phi)
    inclination_factors = calc_inclination_factors(
        phi, cohesion, bearing_capacity_factors, foundation, loading
    )
    depth_factors = calc_depth_factors(foundation, phi)
    base_factors = calc_base_factors(phi, foundation)
    ground_factors = calc_ground_factors(inclination_factors.iq, foundation.slope_angle or 0.0, phi)

    if phi == 0.0:
        q_ult = (
            5.14
            * cohesion
            * (
                1.0
                + shape_factors.sc
                + depth_factors.dc
                - inclination_factors.ic
                - base_factors.bc
                - ground_factors.gc
            )
            + effective_surcharge
        )
    else:
        part_1 = (
            cohesion
            * bearing_capacity_factors.nc
            * shape_factors.sc
            * depth_factors.dc
            * base_factors.bc
            * ground_factors.gc
            * inclination_factors.ic
        )

        part_2 = (
            effective_surcharge
            * bearing_capacity_factors.nq
            * shape_factors.sq
            * depth_factors.dq
            * base_factors.bq
            * ground_factors.gq
            * inclination_factors.iq
        )

        if foundation.effective_width is None:
            raise ValueError("Effective width must be set")

        part_3 = (
            0.5
            * effective_unit_weight
            * foundation.effective_width
            * bearing_capacity_factors.ng
            * shape_factors.sg
            * depth_factors.dg
            * base_factors.bg
            * ground_factors.gg
            * inclination_factors.ig
        )

        q_ult = part_1 + part_2 + part_3

    q_allow = q_ult / factor_of_safety
    is_safe = foundation_pressure <= q_allow

    return BearingCapacityResult(
        bearing_capacity_factors=bearing_capacity_factors,
        shape_factors=shape_factors,
        depth_factors=depth_factors,
        load_inclination_factors=inclination_factors,
        ground_factors=ground_factors,
        base_factors=base_factors,
        soil_params=soil_params,
        ultimate_bearing_capacity=q_ult,
        allowable_bearing_capacity=q_allow,
        is_safe=is_safe,
        qmax=foundation_pressure,
    )
