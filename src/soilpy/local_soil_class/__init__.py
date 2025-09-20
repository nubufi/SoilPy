"""Local soil classification module for SoilPy."""

from .by_cu import CuLayerData, CuSoilClassificationResult, calc_lsc_by_cu
from .by_spt import NLayerData, SptSoilClassificationResult, calc_lsc_by_spt
from .by_vs import VsLayerData, VsSoilClassificationResult, calc_lsc_by_vs

__all__ = [
    "calc_lsc_by_cu",
    "CuLayerData",
    "CuSoilClassificationResult",
    "calc_lsc_by_spt",
    "NLayerData",
    "SptSoilClassificationResult",
    "calc_lsc_by_vs",
    "VsLayerData",
    "VsSoilClassificationResult",
]
