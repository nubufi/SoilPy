"""Bearing capacity model definitions for SoilPy."""

from dataclasses import dataclass


@dataclass
class BearingCapacityFactors:
    """Bearing capacity factors according to Terzaghi, Meyerhof, Hansen, etc."""

    nc: float
    nq: float
    ng: float  # sometimes denoted as Nγ


@dataclass
class ShapeFactors:
    """Shape modification factors used in bearing capacity equations."""

    sc: float
    sq: float
    sg: float


@dataclass
class InclinationFactors:
    """Inclination modification factors for inclined load conditions."""

    ic: float
    iq: float
    ig: float


@dataclass
class BaseFactors:
    """Base inclination factors depending on foundation base angle."""

    bc: float
    bq: float
    bg: float


@dataclass
class GroundFactors:
    """Ground slope modification factors affecting bearing capacity."""

    gc: float
    gq: float
    gg: float


@dataclass
class DepthFactors:
    """Depth modification factors for accounting foundation embedment."""

    dc: float
    dq: float
    dg: float


@dataclass
class SoilParams:
    """Soil parameters used in bearing capacity calculations."""

    friction_angle: float
    cohesion: float
    unit_weight: float


@dataclass
class BearingCapacityResult:
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
