"""Models for consolidation settlement calculations."""

from dataclasses import dataclass
from typing import List


@dataclass
class SettlementResult:
    """Represents the consolidation settlement calculation result."""

    settlement_per_layer: List[float]  # Settlement for each layer in cm
    total_settlement: float  # Total settlement in cm
    qnet: float  # Net foundation pressure in t/m²
