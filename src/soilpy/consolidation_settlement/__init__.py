"""Consolidation settlement module for SoilPy."""

from .by_compression_index import (
    calc_settlement as calc_settlement_by_compression_index,
)
from .by_mv import calc_settlement as calc_settlement_by_mv
from .model import SettlementResult

__all__ = [
    "SettlementResult",
    "calc_settlement_by_compression_index",
    "calc_settlement_by_mv",
]
