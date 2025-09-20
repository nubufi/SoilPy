"""Helper functions for consolidation settlement calculations."""

import math
from typing import Tuple

from soilpy.models import SoilProfile


def get_center_and_thickness(
    soil_profile: SoilProfile,
    df: float,
    layer_index: int,
) -> Tuple[float, float]:
    """Calculates the center and thickness of a soil layer based on the ground water table (GWT) and the depth of the foundation (df).

    Args:
        soil_profile: The soil profile containing the layers
        df: The depth of the foundation
        layer_index: The index of the layer

    Returns:
        A tuple containing the center and thickness of the layer
    """
    if soil_profile.ground_water_level is None:
        raise ValueError("Ground water level must be set")

    gwt = soil_profile.ground_water_level
    gwt_layer_index = soil_profile.get_layer_index(gwt)
    df_layer_index = soil_profile.get_layer_index(df)
    layer = soil_profile.layers[layer_index]

    if layer.thickness is None:
        raise ValueError("Layer thickness must be set")

    if gwt_layer_index < layer_index:
        if layer_index == df_layer_index:
            thickness = layer.thickness - df
            center = df + thickness / 2.0
            return (center, thickness)
        else:
            thickness = layer.thickness
            if layer.center is None:
                raise ValueError("Layer center must be set")
            center = layer.center
            return (center, thickness)
    else:
        max_depth = max(df, gwt)
        thickness = layer.thickness - max_depth
        center = max_depth + thickness / 2.0
        return (center, thickness)


def calc_delta_stress(q: float, width: float, length: float, center: float) -> float:
    """Calculates the change in effective stress (delta_stress) based on the foundation pressure (q),
    width, length, and center of the layer.

    Args:
        q: Foundation pressure [t/m²]
        width: Width of the foundation [m]
        length: Length of the foundation [m]
        center: Center of the layer [m]

    Returns:
        Change in effective stress [t/m²]
    """
    return q * width * length / ((width + center) * (length + center))
