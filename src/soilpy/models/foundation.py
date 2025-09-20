"""Foundation model for SoilPy."""

from dataclasses import dataclass
from typing import Optional

from ..validation import ValidationError, validate_field


@dataclass
class Foundation:
    """Represents a foundation with geometry and load effects.

    Attributes:
        foundation_depth: Depth of the foundation (m)
        foundation_length: Length of the foundation (m)
        foundation_width: Width of the foundation (m)
        foundation_area: Area of the foundation (m²)
        effective_length: Effective length of the foundation after load effects (m)
        effective_width: Effective width of the foundation after load effects (m)
        base_tilt_angle: Foundation inclination angle (degrees)
        slope_angle: Slope angle of the ground (degrees)
        surface_friction_coefficient: Friction coefficient for horizontal sliding (unitless)
    """

    foundation_depth: Optional[float] = None
    foundation_length: Optional[float] = None
    foundation_width: Optional[float] = None
    foundation_area: Optional[float] = None
    base_tilt_angle: Optional[float] = None
    slope_angle: Optional[float] = None
    effective_length: Optional[float] = None
    effective_width: Optional[float] = None
    surface_friction_coefficient: Optional[float] = None

    @classmethod
    def new(
        cls,
        depth: Optional[float] = None,
        length: Optional[float] = None,
        width: Optional[float] = None,
        angle: Optional[float] = None,
        slope: Optional[float] = None,
        area: Optional[float] = None,
        surface_friction_coefficient: Optional[float] = None,
    ) -> "Foundation":
        """Creates a new Foundation instance.

        Args:
            depth: Depth of the foundation (m)
            length: Length of the foundation (m)
            width: Width of the foundation (m)
            angle: Foundation inclination angle (degrees)
            slope: Slope angle of the ground (degrees)
            area: Area of the foundation (m²)
            surface_friction_coefficient: Friction coefficient for horizontal sliding

        Returns:
            A new Foundation instance
        """
        return cls(
            foundation_depth=depth,
            foundation_length=length,
            foundation_width=width,
            foundation_area=area,
            base_tilt_angle=angle,
            slope_angle=slope,
            effective_length=None,
            effective_width=None,
            surface_friction_coefficient=surface_friction_coefficient,
        )

    def calc_effective_lengths(self, ex: float, ey: float) -> None:
        """Calculates effective lengths based on applied loads.

        Args:
            ex: Eccentricity in x-direction (m)
            ey: Eccentricity in y-direction (m)
        """
        if self.foundation_width is None or self.foundation_length is None:
            raise ValueError(
                "Foundation width and length must be set before calculating effective lengths"
            )

        b_ = self.foundation_width - 2.0 * ex
        l_ = self.foundation_length - 2.0 * ey

        self.effective_width = max(min(b_, l_), 0.0)
        self.effective_length = max(max(b_, l_), 0.0)

    def validate(self, fields: list[str]) -> None:
        """Validates specific fields of the Foundation using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        for field in fields:
            if field == "foundation_depth":
                validate_field(
                    "foundation_depth",
                    self.foundation_depth,
                    0.0,
                    error_code_prefix="foundation",
                )
            elif field == "foundation_length":
                validate_field(
                    "foundation_length",
                    self.foundation_length,
                    0.0001,
                    error_code_prefix="foundation",
                )
            elif field == "foundation_width":
                validate_field(
                    "foundation_width",
                    self.foundation_width,
                    0.001,
                    self.foundation_length,
                    error_code_prefix="foundation",
                )
            elif field == "foundation_area":
                validate_field(
                    "foundation_area",
                    self.foundation_area,
                    0.001,
                    error_code_prefix="foundation",
                )
            elif field == "base_tilt_angle":
                validate_field(
                    "base_tilt_angle",
                    self.base_tilt_angle,
                    0.0,
                    45.0,
                    error_code_prefix="foundation",
                )
            elif field == "slope_angle":
                validate_field(
                    "slope_angle",
                    self.slope_angle,
                    0.0,
                    90.0,
                    error_code_prefix="foundation",
                )
            elif field == "effective_width":
                validate_field(
                    "effective_width",
                    self.effective_width,
                    0.0,
                    error_code_prefix="foundation",
                )
            elif field == "effective_length":
                validate_field(
                    "effective_length",
                    self.effective_length,
                    0.0,
                    error_code_prefix="foundation",
                )
            elif field == "surface_friction_coefficient":
                validate_field(
                    "surface_friction_coefficient",
                    self.surface_friction_coefficient,
                    0.0,
                    1.0,
                    error_code_prefix="foundation",
                )
            else:
                raise ValidationError(
                    code="foundation.invalid_field",
                    message=f"Field '{field}' is not valid for Foundation.",
                )
