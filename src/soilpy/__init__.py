"""SoilPy - A geotechnical engineering library for soil mechanics calculations."""

__version__ = "0.7.10"
__author__ = "Numan Burak Fidan"

# Import main modules
from . import (
    bearing_capacity,
    consolidation_settlement,
    effective_depth,
    elastic_settlement,
    helper,
    horizontal_sliding,
    liquefaction,
    local_soil_class,
    models,
    soil_coefficient,
    swelling_potential,
    validation,
)

__all__ = [
    "models",
    "bearing_capacity",
    "consolidation_settlement",
    "effective_depth",
    "elastic_settlement",
    "horizontal_sliding",
    "liquefaction",
    "local_soil_class",
    "soil_coefficient",
    "swelling_potential",
    "validation",
    "helper",
]
