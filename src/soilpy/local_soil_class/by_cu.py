"""Local soil classification by Cu (undrained shear strength) for SoilPy."""

from dataclasses import dataclass
from typing import List

from soilpy.models import SoilProfile
from soilpy.validation import ValidationError


@dataclass
class CuLayerData:
    """Data for a single layer in Cu-based soil classification."""

    thickness: float  # Layer thickness (h) in meters
    cu: float  # Undrained shear strength (Cu) in t/m²
    h_over_cu: float  # H/Cu ratio


@dataclass
class CuSoilClassificationResult:
    """Result of Cu-based soil classification."""

    layers: List[CuLayerData]  # Per-layer Cu information
    sum_h_over_cu: float  # Sum of h/Cu values across all layers (unit: m / (t/m²))
    cu_30: float  # (Cu)_30 value calculated from the layers
    soil_class: str  # Final local soil class (e.g., ZE, ZD, ZC)


def validate_input(soil_profile: SoilProfile) -> None:
    """Validates the input data for local soil classification calculations.

    Args:
        soil_profile: The soil profile data

    Raises:
        ValidationError: If validation fails
    """
    soil_profile.validate(["thickness", "cu"])


def compute_cu_30(profile: SoilProfile) -> List[CuLayerData]:
    """Calculates (cu)_30 based on the harmonic average over the top 30m of the profile.

    Args:
        profile: The soil profile

    Returns:
        List of CuLayerData for the top 30m
    """
    remaining_depth = 30.0
    result: List[CuLayerData] = []

    for layer in profile.layers:
        if remaining_depth <= 0.0:
            break

        if layer.thickness is None:
            continue

        thickness = min(layer.thickness, remaining_depth)
        cu = layer.cu or 0.0

        if cu <= 0.0:
            continue  # Skip layer with Cu == 0

        h_over_cu = thickness / cu
        result.append(
            CuLayerData(
                thickness=thickness,
                cu=cu,
                h_over_cu=h_over_cu,
            )
        )

        remaining_depth -= thickness

    return result


def calc_lsc_by_cu(soil_profile: SoilProfile) -> CuSoilClassificationResult:
    """Calculates the local soil class (ZE, ZD, ZC) based on the harmonic average of Cu values
    over the top 30m of the profile.

    Args:
        soil_profile: A SoilProfile object

    Returns:
        CuSoilClassificationResult: A result containing the calculated local soil class and other related data

    Raises:
        ValidationError: If validation fails
    """
    validate_input(soil_profile)
    soil_profile.calc_layer_depths()
    cu_layers = compute_cu_30(soil_profile)

    sum_h_over_cu = sum(layer.h_over_cu for layer in cu_layers)

    if not soil_profile.layers or soil_profile.layers[-1].depth is None:
        raise ValueError("Soil profile must have layers with depth information")

    depth = min(soil_profile.layers[-1].depth, 30.0)

    cu_30 = depth / sum_h_over_cu if sum_h_over_cu > 0.0 else 0.0

    if cu_30 > 25.0:
        soil_class = "ZC"
    elif cu_30 >= 7.0:
        soil_class = "ZD"
    else:
        soil_class = "ZE"

    return CuSoilClassificationResult(
        layers=cu_layers,
        sum_h_over_cu=sum_h_over_cu,
        cu_30=cu_30,
        soil_class=soil_class,
    )
