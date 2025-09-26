"""Loads model for SoilPy."""

from typing import Optional

from pydantic import BaseModel, Field

from ..enums import LoadCase, SelectionMethod
from ..validation import ValidationError, validate_field


class Stress(BaseModel):
    """Stress values in ton/m^2."""

    min: Optional[float] = None
    avg: Optional[float] = None
    max: Optional[float] = None

    def validate(self) -> None:
        """Validates the stress values."""
        validate_field("min", self.min, error_code_prefix="loads")
        validate_field("avg", self.avg, error_code_prefix="loads")
        validate_field("max", self.max, error_code_prefix="loads")


class Loads(BaseModel):
    """Loading conditions for foundation design."""

    service_load: Optional[Stress] = None
    ultimate_load: Optional[Stress] = None
    seismic_load: Optional[Stress] = None
    horizontal_load_x: Optional[float] = None
    horizontal_load_y: Optional[float] = None
    moment_x: Optional[float] = None
    moment_y: Optional[float] = None
    vertical_load: Optional[float] = None

    def get_vertical_stress(
        self, load_case: LoadCase, load_severity: SelectionMethod
    ) -> float:
        """Get vertical stress value in ton/m^2 for specified load_case and load_severity.

        Args:
            load_case: Load case
            load_severity: Load severity

        Returns:
            Vertical stress value in ton/m^2
        """
        if load_case == LoadCase.SERVICE_LOAD:
            if self.service_load is None:
                return 0.0
            if load_severity == SelectionMethod.MIN:
                return self.service_load.min or 0.0
            elif load_severity == SelectionMethod.AVG:
                return self.service_load.avg or 0.0
            else:  # MAX
                return self.service_load.max or 0.0

        elif load_case == LoadCase.ULTIMATE_LOAD:
            if self.ultimate_load is None:
                return 0.0
            if load_severity == SelectionMethod.MIN:
                return self.ultimate_load.min or 0.0
            elif load_severity == SelectionMethod.AVG:
                return self.ultimate_load.avg or 0.0
            else:  # MAX
                return self.ultimate_load.max or 0.0

        else:  # SEISMIC_LOAD
            if self.seismic_load is None:
                return 0.0
            if load_severity == SelectionMethod.MIN:
                return self.seismic_load.min or 0.0
            elif load_severity == SelectionMethod.AVG:
                return self.seismic_load.avg or 0.0
            else:  # MAX
                return self.seismic_load.max or 0.0

    def calc_eccentricity(self) -> tuple[float, float]:
        """Calculates the eccentricity of the loading.

        Returns:
            Tuple of (ex, ey) - Eccentricities in meters

        Note:
            If vertical_load is zero, it returns (0.0, 0.0) to prevent division by zero.
        """
        if self.vertical_load is None or self.vertical_load == 0.0:
            return (0.0, 0.0)

        if self.moment_x is not None and self.moment_y is not None:
            ex = self.moment_x / self.vertical_load
            ey = self.moment_y / self.vertical_load
            return (ex, ey)

        return (0.0, 0.0)

    def validate(self, fields: list[str]) -> None:
        """Validates specific fields of the Loads using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        for field in fields:
            if field == "horizontal_load_x":
                validate_field(
                    "horizontal_load_x",
                    self.horizontal_load_x,
                    0.0,
                    error_code_prefix="loads",
                )
            elif field == "horizontal_load_y":
                validate_field(
                    "horizontal_load_y",
                    self.horizontal_load_y,
                    0.0,
                    error_code_prefix="loads",
                )
            elif field == "moment_x":
                validate_field(
                    "moment_x", self.moment_x, 0.0, error_code_prefix="loads"
                )
            elif field == "moment_y":
                validate_field(
                    "moment_y", self.moment_y, 0.0, error_code_prefix="loads"
                )
            elif field == "vertical_load":
                validate_field(
                    "vertical_load", self.vertical_load, 0.0, error_code_prefix="loads"
                )
            elif field == "service_load":
                if self.service_load is None:
                    raise ValidationError(
                        code="loads.service_load_not_set",
                        message="Service load is not set.",
                    )
                self.service_load.validate()
            elif field == "ultimate_load":
                if self.ultimate_load is None:
                    raise ValidationError(
                        code="loads.ultimate_load_not_set",
                        message="Ultimate load is not set.",
                    )
                self.ultimate_load.validate()
            elif field == "seismic_load":
                if self.seismic_load is None:
                    raise ValidationError(
                        code="loads.seismic_load_not_set",
                        message="Seismic load is not set.",
                    )
                self.seismic_load.validate()
            else:
                raise ValidationError(
                    code="loads.invalid_field",
                    message=f"Field '{field}' is not valid for Loads.",
                )
