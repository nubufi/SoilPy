"""Point Load Test model for SoilPy."""

from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from ..enums import SelectionMethod
from ..validation import ValidationError, validate_field


class PointLoadSample(BaseModel):
    """Represents an individual Point Load Test sample for determining rock strength.

    Attributes:
        depth: Depth of the sample in meters
        sample_no: Optional identifier number for the tested sample
        p: Optional applied load at failure in kiloNewtons (kN)
        is: Optional point load strength index in MegaPascals (MPa)
        f: Optional size correction factor
        is50: Corrected point load strength index to 50 mm diameter in MegaPascals (MPa)
        l: Optional distance between load application points in millimeters (mm)
        d: Equivalent core diameter in millimeters (mm)
    """

    depth: Optional[float] = None
    sample_no: Optional[int] = None
    p: Optional[float] = None
    is_value: Optional[float] = None
    f: Optional[float] = None
    is50: Optional[float] = None
    l: Optional[float] = None
    d: Optional[float] = None

    @classmethod
    def new(cls, depth: float, is50: float, d: float) -> "PointLoadSample":
        """Creates a new PointLoadSample instance.

        Args:
            depth: Depth of the sample in meters
            is50: Corrected point load strength index to 50 mm diameter in MPa
            d: Equivalent core diameter in millimeters

        Returns:
            A new PointLoadSample instance
        """
        return cls(depth=depth, is50=is50, d=d)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the PointLoadSample using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        for field in fields:
            if field == "depth":
                validate_field(
                    "depth", self.depth, 0.0, error_code_prefix="point_load_test"
                )
            elif field == "sample_no":
                validate_field(
                    "sample_no", self.sample_no, 0, error_code_prefix="point_load_test"
                )
            elif field == "p":
                validate_field("p", self.p, 0.0001, error_code_prefix="point_load_test")
            elif field == "is":
                validate_field(
                    "is", self.is_value, 0.00001, error_code_prefix="point_load_test"
                )
            elif field == "f":
                validate_field(
                    "f", self.f, 0.00001, error_code_prefix="point_load_test"
                )
            elif field == "is50":
                validate_field(
                    "is50", self.is50, 0.00001, error_code_prefix="point_load_test"
                )
            elif field == "l":
                validate_field(
                    "l", self.l, 0.00001, error_code_prefix="point_load_test"
                )
            elif field == "d":
                validate_field(
                    "d", self.d, 0.00001, error_code_prefix="point_load_test"
                )
            else:
                raise ValidationError(
                    code="point_load_test.invalid_field",
                    message=f"Field '{field}' is not valid for Point Load Test.",
                )


class PointLoadExp(BaseModel):
    """Represents a single borehole containing multiple Point Load Test samples.

    Attributes:
        borehole_id: Identifier for the borehole
        samples: Collection of Point Load Test samples taken from the borehole
    """

    borehole_id: str = ""
    samples: List[PointLoadSample] = Field(default_factory=list)

    @classmethod
    def new(cls, borehole_id: str, samples: List[PointLoadSample]) -> "PointLoadExp":
        """Creates a new PointLoadExp instance.

        Args:
            borehole_id: Identifier for the borehole
            samples: Collection of Point Load Test samples

        Returns:
            A new PointLoadExp instance
        """
        return cls(borehole_id=borehole_id, samples=samples)

    def add_sample(self, sample: PointLoadSample) -> None:
        """Adds a new sample to the experiment.

        Args:
            sample: The PointLoadSample to add
        """
        self.samples.append(sample)

    def get_sample_at_depth(self, depth: float) -> PointLoadSample:
        """Retrieves the sample at the specified depth.

        This function finds the first sample whose depth is greater than or equal to the given depth.
        If no such sample is found, it returns the last sample in the list.

        Args:
            depth: The depth at which to search for an experiment sample

        Returns:
            The matching PointLoadSample
        """
        for sample in self.samples:
            if sample.depth is not None and sample.depth >= depth:
                return sample
        return self.samples[-1] if self.samples else PointLoadSample()

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the PointLoadExp using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.samples:
            raise ValidationError(
                code="point_load_test.empty_samples",
                message="No samples provided for Point Load Experiment.",
            )

        for sample in self.samples:
            sample.validate(fields)


class PointLoadTest(BaseModel):
    """Represents the entire Point Load Test comprising multiple boreholes.

    Attributes:
        exps: Collection of borehole tests included in the overall test campaign
        idealization_method: Method used for idealizing the test results
    """

    exps: List[PointLoadExp] = Field(default_factory=list)
    idealization_method: SelectionMethod = SelectionMethod.AVG

    @classmethod
    def new(
        cls, exps: List[PointLoadExp], idealization_method: SelectionMethod
    ) -> "PointLoadTest":
        """Creates a new PointLoadTest instance.

        Args:
            exps: Collection of borehole tests
            idealization_method: Method used for idealizing the test results

        Returns:
            A new PointLoadTest instance
        """
        return cls(exps=exps, idealization_method=idealization_method)

    def add_borehole(self, exp: PointLoadExp) -> None:
        """Adds a new borehole to the test.

        Args:
            exp: The PointLoadExp to add
        """
        self.exps.append(exp)

    def get_idealized_exp(self, name: str) -> PointLoadExp:
        """Get the idealized experiment.

        Args:
            name: Name of the idealized experiment

        Returns:
            PointLoadExp: Idealized experiment
        """
        if not self.exps:
            return PointLoadExp.new(name, [])

        mode = self.idealization_method
        depth_map = {}

        # Collect all unique depths and corresponding (is50, d) values
        for exp in self.exps:
            for sample in exp.samples:
                if (
                    sample.depth is not None
                    and sample.is50 is not None
                    and sample.d is not None
                ):
                    depth = sample.depth
                    if depth not in depth_map:
                        depth_map[depth] = []
                    depth_map[depth].append((sample.is50, sample.d))

        # Create a new PointLoadExp with selected values
        idealized_samples = []

        for depth, is50_d_pairs in depth_map.items():
            if mode == SelectionMethod.MIN:
                selected_is50, selected_d = min(is50_d_pairs, key=lambda x: x[0])
            elif mode == SelectionMethod.MAX:
                selected_is50, selected_d = max(is50_d_pairs, key=lambda x: x[0])
            else:  # AVG
                sum_is50 = sum(pair[0] for pair in is50_d_pairs)
                sum_d = sum(pair[1] for pair in is50_d_pairs)
                count = len(is50_d_pairs)
                selected_is50 = sum_is50 / count
                selected_d = sum_d / count

            idealized_samples.append(
                PointLoadSample.new(depth, selected_is50, selected_d)
            )

        return PointLoadExp.new(name, idealized_samples)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the PointLoadTest using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.exps:
            raise ValidationError(
                code="point_load_test.empty_exps",
                message="No experiments provided for Point Load Test.",
            )

        for exp in self.exps:
            exp.validate(fields)
