"""Models for liquefaction analysis in SoilPy."""

from dataclasses import dataclass, field
from typing import List, Optional

from soilpy.models import SoilLayer, SPTExp


@dataclass
class CommonLiquefactionLayerResult:
    """Result of liquefaction analysis for a single layer."""

    soil_layer: SoilLayer = field(default_factory=SoilLayer)
    depth: float = 0.0
    normal_stress: float = 0.0
    effective_stress: float = 0.0
    crr: Optional[float] = None
    crr75: Optional[float] = None
    csr: Optional[float] = None
    safety_factor: Optional[float] = None
    is_safe: bool = True
    settlement: float = 0.0
    rd: float = 0.0


@dataclass
class VSLiquefactionLayerResult:
    """Result of liquefaction analysis for a single layer."""

    vs: float
    vs1: Optional[float] = None
    vs1c: Optional[float] = None
    cn: Optional[float] = None


@dataclass
class VSLiquefactionResult:
    """Result of liquefaction analysis for entire soil profile."""

    layers: List[CommonLiquefactionLayerResult]  # All layer results
    vs_layers: List[VSLiquefactionLayerResult]  # VS layer results
    total_settlement: float  # Sum of settlements
    msf: float  # Magnitude Scaling Factor


@dataclass
class SptLiquefactionResult:
    """Result of liquefaction analysis for entire soil profile."""

    layers: List[CommonLiquefactionLayerResult]  # All layer results
    spt_exp: SPTExp
    total_settlement: float  # Sum of settlements
    msf: float  # Magnitude Scaling Factor
