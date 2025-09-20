"""Local soil classification by SPT (Standard Penetration Test) for SoilPy."""

from dataclasses import dataclass
from typing import List

from soilpy.models import SPT, SPTExp
from soilpy.validation import ValidationError


@dataclass
class NLayerData:
    """Data for a single layer in SPT-based soil classification."""

    thickness: float  # Layer thickness (h) in meters
    n: float  # N-value (N60 or N1_60f) in blows/30cm
    h_over_n: float  # H/N ratio


@dataclass
class SptSoilClassificationResult:
    """Result of SPT-based soil classification."""

    layers: List[NLayerData]  # Per-layer N information
    sum_h_over_n: float  # Sum of h/N values across all layers (unit: m / blows)
    n_30: float  # (N)_30 value calculated from the layers
    soil_class: str  # Final local soil class (e.g., ZE, ZD, ZC)


def validate_input(spt: SPT) -> None:
    """Validates the soil profile and SPT data.

    Args:
        spt: SPT data

    Raises:
        ValidationError: If validation fails
    """
    spt.validate(["n", "depth"])


def prepare_spt_exp(spt: SPT) -> SPTExp:
    """Prepares the SPTExp object by calculating all N values and applying energy correction.

    Args:
        spt: A SPT object containing the SPT data

    Returns:
        SPTExp: The prepared SPTExp object with calculated N values and applied corrections
    """
    spt_exp = spt.get_idealized_exp("idealized")
    spt_exp.apply_energy_correction(spt.energy_correction_factor)

    return spt_exp


def compute_n_30(spt_exp: SPTExp) -> List[NLayerData]:
    """Calculates (N60)_30 based on the harmonic average over the top 30m of the profile.

    Args:
        spt_exp: SPT experiment data

    Returns:
        List of NLayerData for the top 30m
    """
    result: List[NLayerData] = []
    remaining_depth = 30.0
    blows = spt_exp.blows

    for i, blow in enumerate(blows):
        if remaining_depth <= 0.0:
            break

        previous_depth = 0.0 if i == 0 else blows[i - 1].depth
        thickness = min(blow.depth - previous_depth, remaining_depth)

        if thickness <= 0.0:
            continue  # Skip invalid thickness

        # Handle None n60 values
        if blow.n60 is None:
            continue  # Skip missing n values

        n = blow.n60.to_i32()  # Refusal handled inside to_i32()

        if n <= 0.0:
            continue  # Skip invalid or missing n values

        h_over_n = thickness / n

        result.append(
            NLayerData(
                thickness=thickness,
                n=n,
                h_over_n=h_over_n,
            )
        )

        remaining_depth -= thickness

    return result


def calc_lsc_by_spt(spt: SPT) -> SptSoilClassificationResult:
    """Calculates the local soil class (ZE, ZD, ZC) based on the harmonic average of N60 values
    over the top 30m of the profile.

    Args:
        spt: A SPT object containing the SPT data

    Returns:
        SptSoilClassificationResult: A result containing the calculated local soil class and other related data

    Raises:
        ValidationError: If validation fails
    """
    validate_input(spt)
    spt_exp = prepare_spt_exp(spt)
    n_layers = compute_n_30(spt_exp)

    sum_h_over_n = sum(layer.h_over_n for layer in n_layers)
    depth = min(spt_exp.blows[-1].depth, 30.0)

    n_30 = depth / sum_h_over_n if sum_h_over_n > 0.0 else 0.0

    if n_30 > 50.0:
        soil_class = "ZC"
    elif n_30 >= 15.0:
        soil_class = "ZD"
    else:
        soil_class = "ZE"

    return SptSoilClassificationResult(
        layers=n_layers,
        sum_h_over_n=sum_h_over_n,
        n_30=n_30,
        soil_class=soil_class,
    )
