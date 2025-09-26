"""Models for liquefaction analysis in SoilPy."""

from typing import List, Optional

from pydantic import BaseModel, Field

from soilpy.models import SoilLayer, SPTExp


class CommonLiquefactionLayerResult(BaseModel):
    """Result of liquefaction analysis for a single layer."""

    soil_layer: SoilLayer = Field(default_factory=SoilLayer)
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


class VSLiquefactionLayerResult(BaseModel):
    """Result of liquefaction analysis for a single layer."""

    vs: float
    vs1: Optional[float] = None
    vs1c: Optional[float] = None
    cn: Optional[float] = None


class VSLiquefactionResult(BaseModel):
    """Result of liquefaction analysis for entire soil profile."""

    layers: List[CommonLiquefactionLayerResult]  # All layer results
    vs_layers: List[VSLiquefactionLayerResult]  # VS layer results
    total_settlement: float  # Sum of settlements
    msf: float  # Magnitude Scaling Factor


class SptLiquefactionResult(BaseModel):
    """Result of liquefaction analysis for entire soil profile."""

    layers: List[CommonLiquefactionLayerResult]  # All layer results
    spt_exp: SPTExp
    total_settlement: float  # Sum of settlements
    msf: float  # Magnitude Scaling Factor
