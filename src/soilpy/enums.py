"""Enums module for SoilPy."""

from enum import Enum


class SelectionMethod(Enum):
    """Selection method for choosing values."""

    MIN = "Min"
    AVG = "Avg"
    MAX = "Max"


class LoadCase(Enum):
    """Load cases for foundation design.

    Variants:
    - SERVICE_LOAD: Service load case (G + Q)
    - ULTIMATE_LOAD: Ultimate load case (1.4G + 1.6Q)
    - SEISMIC_LOAD: Seismic load case (G + Q + E/0.9G + E)

    Note:
    - G: Dead load
    - Q: Live load
    - E: Earthquake load
    """

    SERVICE_LOAD = "ServiceLoad"
    ULTIMATE_LOAD = "UltimateLoad"
    SEISMIC_LOAD = "SeismicLoad"


class AnalysisTerm(Enum):
    """Analysis term for calculations.

    Variants:
    - SHORT: Short term analysis
    - LONG: Long term analysis
    """

    SHORT = "Short"
    LONG = "Long"
