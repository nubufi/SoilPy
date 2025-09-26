"""Bearing capacity model definitions for SoilPy."""

from pydantic import BaseModel


class BearingCapacityFactors(BaseModel):
    """Bearing capacity factors according to Terzaghi, Meyerhof, Hansen, etc."""

    nc: float
    nq: float
    ng: float  # sometimes denoted as Nγ


class ShapeFactors(BaseModel):
    """Shape modification factors used in bearing capacity equations."""

    sc: float
    sq: float
    sg: float


class InclinationFactors(BaseModel):
    """Inclination modification factors for inclined load conditions."""

    ic: float
    iq: float
    ig: float


class BaseFactors(BaseModel):
    """Base inclination factors depending on foundation base angle."""

    bc: float
    bq: float
    bg: float


class GroundFactors(BaseModel):
    """Ground slope modification factors affecting bearing capacity."""

    gc: float
    gq: float
    gg: float


class DepthFactors(BaseModel):
    """Depth modification factors for accounting foundation embedment."""

    dc: float
    dq: float
    dg: float


class SoilParams(BaseModel):
    """Soil parameters used in bearing capacity calculations."""

    friction_angle: float
    cohesion: float
    unit_weight: float


class BearingCapacityResult(BaseModel):
    """Result of bearing capacity calculation."""

    bearing_capacity_factors: BearingCapacityFactors
    shape_factors: ShapeFactors
    depth_factors: DepthFactors
    load_inclination_factors: InclinationFactors
    ground_factors: GroundFactors
    base_factors: BaseFactors
    soil_params: SoilParams
    ultimate_bearing_capacity: float
    allowable_bearing_capacity: float
    is_safe: bool
    qmax: float
