"""Models for consolidation settlement calculations."""

from typing import List

from pydantic import BaseModel


class SettlementResult(BaseModel):
    """Represents the consolidation settlement calculation result."""

    settlement_per_layer: List[float]  # Settlement for each layer in cm
    total_settlement: float  # Total settlement in cm
    qnet: float  # Net foundation pressure in t/m²
