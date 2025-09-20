"""Local soil classification by VS (Shear Wave Velocity) for SoilPy."""

from dataclasses import dataclass
from typing import List

from soilpy.models import Masw, MaswExp
from soilpy.validation import ValidationError


@dataclass
class VsLayerData:
    """Data for a single layer in VS-based soil classification."""

    thickness: float  # Layer thickness (h) in meters
    vs: float  # Shear wave velocity (Vs) in m/s
    h_over_vs: float  # H/Vs ratio


@dataclass
class VsSoilClassificationResult:
    """Result of VS-based soil classification."""

    layers: List[VsLayerData]  # Per-layer Vs information
    sum_h_over_vs: float  # Sum of h/Vs values across all layers (unit: m / (m/s))
    vs_30: float  # (Vs)_30 value calculated from the layers
    soil_class: str  # Final local soil class (e.g., ZE, ZD, ZC, ZB, ZA)


def validate_input(masw: Masw) -> None:
    """Validates the input data for local soil class calculations.

    Args:
        masw: The MASW data

    Raises:
        ValidationError: If validation fails
    """
    masw.validate(["thickness", "vs"])


def compute_vs_30(masw_exp: MaswExp) -> List[VsLayerData]:
    """Calculates (vs)_30 based on the harmonic average over the top 30m of the profile.

    Args:
        masw_exp: MASW experiment data

    Returns:
        List of VsLayerData for the top 30m
    """
    remaining_depth = 30.0
    result: List[VsLayerData] = []

    for layer in masw_exp.layers:
        if remaining_depth <= 0.0:
            break

        if layer.thickness is None or layer.vs is None:
            continue

        thickness = min(layer.thickness, remaining_depth)
        vs = layer.vs

        if vs <= 0.0:
            continue  # Skip layer with vs == 0

        h_over_vs = thickness / vs
        result.append(
            VsLayerData(
                thickness=thickness,
                vs=vs,
                h_over_vs=h_over_vs,
            )
        )

        remaining_depth -= thickness

    return result


def calc_lsc_by_vs(masw: Masw) -> VsSoilClassificationResult:
    """Calculates the local soil class (ZE, ZD, ZC, ZB, ZA) based on the harmonic average of Vs values
    over the top 30m of the profile.

    Args:
        masw: A Masw object containing the masw data

    Returns:
        VsSoilClassificationResult: A result containing the calculated local soil class and other related data

    Raises:
        ValidationError: If validation fails
    """
    validate_input(masw)
    masw_exp = masw.get_idealized_exp("idealized")
    masw_exp.calc_depths()

    vs_layers = compute_vs_30(masw_exp)

    sum_h_over_vs = sum(layer.h_over_vs for layer in vs_layers)

    if not masw_exp.layers or masw_exp.layers[-1].depth is None:
        raise ValueError("MASW experiment must have layers with depth information")

    depth = min(masw_exp.layers[-1].depth, 30.0)

    vs_30 = depth / sum_h_over_vs if sum_h_over_vs > 0.0 else 0.0

    if vs_30 > 1500.0:
        soil_class = "ZA"
    elif vs_30 >= 760.0:
        soil_class = "ZB"
    elif vs_30 >= 360.0:
        soil_class = "ZC"
    elif vs_30 >= 180.0:
        soil_class = "ZD"
    else:
        soil_class = "ZE"

    return VsSoilClassificationResult(
        layers=vs_layers,
        sum_h_over_vs=sum_h_over_vs,
        vs_30=vs_30,
        soil_class=soil_class,
    )
