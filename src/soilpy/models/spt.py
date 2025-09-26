"""SPT (Standard Penetration Test) model for SoilPy."""

import math
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from ..enums import SelectionMethod
from ..validation import ValidationError, validate_field


class NValue:
    """Represents an N-value that can be either a numeric value or refusal."""

    def __init__(self, value: Union[int, str]):
        if isinstance(value, str) and value.upper() == "R":
            self._value = "Refusal"
        elif isinstance(value, int):
            self._value = value
        else:
            raise ValueError("Invalid N-value")

    @classmethod
    def from_i32(cls, n: int) -> "NValue":
        """Converts from int to NValue."""
        if n <= 0:
            raise ValueError("n value must be greater than 0")
        return cls(n)

    def to_i32(self) -> int:
        """Converts to int (50 for refusals)."""
        if self._value == "Refusal":
            return 50
        return self._value

    def to_option(self) -> Optional[int]:
        """Converts to Optional[int], treating Refusal as 50."""
        if self._value == "Refusal":
            return 50
        return self._value

    def mul_by_f64(self, factor: float) -> "NValue":
        """Multiply by a factor."""
        if self._value == "Refusal":
            return NValue("R")
        return NValue(int(math.ceil(self._value * factor)))

    def sum_with(self, other: "NValue") -> "NValue":
        """Sum up with another NValue."""
        if self._value == "Refusal" or other._value == "Refusal":
            return NValue("R")
        return NValue(self._value + other._value)

    def add_f64(self, other: float) -> "NValue":
        """Sum up with a float."""
        if self._value == "Refusal":
            return NValue("R")
        return NValue(int(math.ceil(self._value + other)))

    def __str__(self) -> str:
        if self._value == "Refusal":
            return "R"
        return str(self._value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, NValue):
            return False
        return self._value == other._value

    def __lt__(self, other) -> bool:
        if not isinstance(other, NValue):
            return NotImplemented
        if self._value == "Refusal" and other._value == "Refusal":
            return False
        if self._value == "Refusal":
            return False
        if other._value == "Refusal":
            return True
        return self._value < other._value

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return not self < other


class SPTBlow(BaseModel):
    """Represents a single SPT blow."""

    model_config = {"arbitrary_types_allowed": True}

    thickness: Optional[float] = None
    depth: Optional[float] = None
    n: Optional[NValue] = None
    n60: Optional[NValue] = None
    n90: Optional[NValue] = None
    n1_60: Optional[NValue] = None
    n1_60f: Optional[NValue] = None
    cn: Optional[float] = None
    cr: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None

    @classmethod
    def new(cls, depth: float, n: NValue) -> "SPTBlow":
        """Create a new SPTBlow.

        Args:
            depth: Depth of the blow
            n: N-value of the blow

        Returns:
            A new SPTBlow instance
        """
        return cls(depth=depth, n=n)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the SPTBlow using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        for field in fields:
            if field == "depth":
                validate_field("depth", self.depth, 0.0, error_code_prefix="spt")
            elif field == "thickness":
                validate_field(
                    "thickness", self.thickness, 0.0, error_code_prefix="spt"
                )
            elif field == "n":
                if self.n is None:
                    raise ValidationError(
                        code="spt.n.missing", message="N value is missing in SptBlow"
                    )
                validate_field("n", self.n.to_i32(), 1, error_code_prefix="spt")
            elif field == "n60":
                if self.n60 is None:
                    raise ValidationError(
                        code="spt.n60.missing",
                        message="N60 value is missing in SptBlow",
                    )
                validate_field("n60", self.n60.to_i32(), 1, error_code_prefix="spt")
            else:
                raise ValidationError(
                    code="spt.invalid_field",
                    message=f"Field '{field}' is not valid for SPT.",
                )

    def apply_energy_correction(self, energy_correction_factor: float) -> None:
        """Apply energy correction.

        Args:
            energy_correction_factor: Energy correction factor to convert N value to N60
        """
        if self.n is not None:
            n60 = self.n.mul_by_f64(energy_correction_factor)
            self.n60 = n60
            self.n90 = n60.mul_by_f64(1.5)

    def set_cn(self, sigma_effective: float) -> None:
        """Set overburden correction factor.

        Args:
            sigma_effective: Effective overburden pressure in ton
        """
        self.cn = min(math.sqrt(1.0 / (9.81 * sigma_effective)) * 9.78, 1.7)

    def set_cr(self) -> None:
        """Set rod length correction factor."""
        if self.depth is None:
            self.cr = 1.0
        elif self.depth <= 4.0:
            self.cr = 0.75
        elif self.depth <= 6.0:
            self.cr = 0.85
        elif self.depth <= 10.0:
            self.cr = 0.95
        else:
            self.cr = 1.0

    def set_alpha_beta(self, fine_content: float) -> None:
        """Set alpha and beta factors.

        Args:
            fine_content: Percentage of fine content in soil in percentage
        """
        if fine_content <= 5.0:
            self.alpha = 0.0
            self.beta = 1.0
        elif fine_content <= 35.0:
            self.alpha = math.exp(1.76 - (190.0 / (fine_content**2)))
            self.beta = 0.99 + (fine_content**1.5) / 1000.0
        else:
            self.alpha = 5.0
            self.beta = 1.2

    def apply_corrections(self, soil_profile, cs: float, cb: float, ce: float) -> None:
        """Apply corrections.

        Args:
            soil_profile: Soil profile
            cr: rod length correction factor
            cs: sampler correction factor
            cb: borehole diameter correction factor
            ce: energy correction factor
        """
        self.apply_energy_correction(ce)
        if self.depth is not None:
            self.set_cn(soil_profile.calc_effective_stress(self.depth))
        self.set_cr()
        if self.depth is not None:
            layer = soil_profile.get_layer_at_depth(self.depth)
            fine_content = layer.fine_content or 0.0
            self.set_alpha_beta(fine_content)

        if all(
            x is not None for x in [self.n60, self.cn, self.cr, self.alpha, self.beta]
        ):
            n1_60 = self.n60.mul_by_f64(self.cn * self.cr * cs * cb)
            self.n1_60 = n1_60
            self.n1_60f = n1_60.mul_by_f64(self.beta).add_f64(self.alpha)


class SPTExp(BaseModel):
    """Represents a single SPT experiment."""

    blows: List[SPTBlow] = Field(default_factory=list)
    name: str = ""

    @classmethod
    def new(cls, blows: List[SPTBlow], name: str) -> "SPTExp":
        """Create a new SPTExp.

        Args:
            blows: List of SPTBlow
            name: Name of the experiment

        Returns:
            A new SPTExp instance
        """
        return cls(blows=blows, name=name)

    def apply_energy_correction(self, energy_correction_factor: float) -> None:
        """Apply energy correction.

        Args:
            energy_correction_factor: Energy correction factor to convert N value to N60
        """
        for blow in self.blows:
            blow.apply_energy_correction(energy_correction_factor)

    def add_blow(self, depth: float, n: NValue) -> None:
        """Add a new blow to the experiment.

        Args:
            depth: Depth of the blow
            n: N-value of the blow
        """
        self.blows.append(SPTBlow.new(depth, n))

    def calc_thicknesses(self) -> None:
        """Calculate the thickness of each blow."""
        prev_depth = 0.0
        for blow in self.blows:
            if blow.depth is not None:
                blow.thickness = blow.depth - prev_depth
                prev_depth = blow.depth

    def apply_corrections(self, soil_profile, cs: float, cb: float, ce: float) -> None:
        """Apply corrections.

        Args:
            soil_profile: Soil profile
            cs: sampler correction factor
            cb: borehole diameter correction factor
            ce: energy correction factor
        """
        for blow in self.blows:
            blow.apply_corrections(soil_profile, cs, cb, ce)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the SPTExp using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.blows:
            raise ValidationError(
                code="spt.empty_blows", message="No blows provided for SPTExp."
            )

        for blow in self.blows:
            blow.validate(fields)


class SPT(BaseModel):
    """Represents a collection of SPT tests."""

    exps: List[SPTExp] = Field(default_factory=list)
    energy_correction_factor: Optional[float] = None
    diameter_correction_factor: Optional[float] = None
    sampler_correction_factor: Optional[float] = None
    idealization_method: SelectionMethod = SelectionMethod.AVG

    @classmethod
    def new(
        cls,
        energy_correction_factor: float,
        diameter_correction_factor: float,
        sampler_correction_factor: float,
        idealization_method: SelectionMethod,
    ) -> "SPT":
        """Create a new SPT.

        Args:
            energy_correction_factor: Energy correction factor to convert N value to N60
            diameter_correction_factor: Borehole diameter correction factor
            sampler_correction_factor: Sampler correction factor
            idealization_method: Idealization method to use when combining the layers

        Returns:
            A new SPT instance
        """
        return cls(
            exps=[],
            energy_correction_factor=energy_correction_factor,
            diameter_correction_factor=diameter_correction_factor,
            sampler_correction_factor=sampler_correction_factor,
            idealization_method=idealization_method,
        )

    def apply_energy_correction(self, energy_correction_factor: float) -> None:
        """Apply energy correction.

        Args:
            energy_correction_factor: Energy correction factor to convert N value to N60
        """
        for exp in self.exps:
            exp.apply_energy_correction(energy_correction_factor)

    def add_exp(self, exp: SPTExp) -> None:
        """Add a new experiment to the SPT.

        Args:
            exp: SPTExp
        """
        self.exps.append(exp)

    def get_idealized_exp(self, name: str) -> SPTExp:
        """Get the idealized experiment.

        Args:
            name: Name of the idealized experiment

        Returns:
            SPTExp: Idealized experiment
        """
        mode = self.idealization_method
        depth_map = {}

        # Collect all unique depths and corresponding n values
        for exp in self.exps:
            for blow in exp.blows:
                if blow.depth is not None and blow.n is not None:
                    depth = blow.depth
                    if depth not in depth_map:
                        depth_map[depth] = []
                    depth_map[depth].append(blow.n)

        # Create a new SPTExp with selected values
        idealized_blows = []

        for depth, n_values in depth_map.items():
            if mode == SelectionMethod.MIN:
                selected_n = min(n_values)
            elif mode == SelectionMethod.MAX:
                selected_n = max(n_values)
            else:  # AVG
                sum_val = sum(n.to_option() or 0 for n in n_values)
                count = len(n_values)
                if count > 0:
                    # Use math.ceil for values >= 0.5 to match Rust's round behavior
                    avg_float = sum_val / count
                    if avg_float - int(avg_float) >= 0.5:
                        avg_val = int(avg_float) + 1
                    else:
                        avg_val = int(avg_float)
                    selected_n = NValue.from_i32(avg_val)
                else:
                    selected_n = NValue.from_i32(0)

            idealized_blows.append(SPTBlow(depth=depth, n=selected_n))

        return SPTExp.new(idealized_blows, name)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the SPT using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.exps:
            raise ValidationError(
                code="spt.empty_exps", message="No experiments provided for SPT."
            )

        for exp in self.exps:
            exp.validate(fields)

        validate_field(
            "energy_correction_factor",
            self.energy_correction_factor,
            0.001,
            error_code_prefix="spt",
        )
        validate_field(
            "diameter_correction_factor",
            self.diameter_correction_factor,
            0.001,
            error_code_prefix="spt",
        )
        validate_field(
            "sampler_correction_factor",
            self.sampler_correction_factor,
            0.001,
            error_code_prefix="spt",
        )
