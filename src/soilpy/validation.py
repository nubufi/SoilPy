"""Validation module for SoilPy."""

from typing import Optional, Union

from pydantic import BaseModel


class ValidationError(Exception):
    """Validation error with structured error information."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def validate_field(
    field_name: str,
    value: Optional[Union[int, float]],
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    error_code_prefix: str = "validation",
) -> None:
    """Validates a single optional numeric field against optional bounds.

    Args:
        field_name: A name for the field (e.g. "cu")
        value: Optional value to validate
        min_val: Optional minimum value (inclusive)
        max_val: Optional maximum value (inclusive)
        error_code_prefix: A short prefix for generating the error code, e.g., "layer"

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        raise ValidationError(
            code=f"{error_code_prefix}.{field_name}.missing",
            message=f"{field_name} must be provided.",
        )

    if min_val is not None and value < min_val:
        raise ValidationError(
            code=f"{error_code_prefix}.{field_name}.too_small.{min_val}",
            message=f"{field_name} must be greater than or equal to {min_val}.",
        )

    if max_val is not None and value > max_val:
        raise ValidationError(
            code=f"{error_code_prefix}.{field_name}.too_large.{max_val}",
            message=f"{field_name} must be less than or equal to {max_val}.",
        )
