"""CPT (Cone Penetration Test) model for SoilPy."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ..enums import SelectionMethod
from ..validation import ValidationError, validate_field


class CPTLayer(BaseModel):
    """Represents a single CPT (Cone Penetration Test) data point.

    Each CPTLayer instance holds a depth value (in meters) and a cone_resistance value (in MPa).
    """

    depth: Optional[float] = None  # Depth in meters
    cone_resistance: Optional[float] = None  # Cone resistance (qc) in MPa
    sleeve_friction: Optional[float] = None  # Sleeve friction (fs) in MPa
    pore_pressure: Optional[float] = None  # Pore pressure (u2) in MPa
    friction_ratio: Optional[float] = None  # Friction ratio (Rf) in percentage

    @classmethod
    def new(
        cls, depth: float, qc: float, fs: float, u2: Optional[float] = None
    ) -> "CPTLayer":
        """Creates a new CPTLayer instance.

        Args:
            depth: The depth of the CPT data point in meters
            qc: The cone resistance of the CPT data point in MPa
            fs: The sleeve friction of the CPT data point in MPa
            u2: The pore pressure of the CPT data point in MPa

        Returns:
            A new CPTLayer instance
        """
        return cls(
            depth=depth,
            cone_resistance=qc,
            sleeve_friction=fs,
            pore_pressure=u2,
            friction_ratio=None,
        )

    def calc_friction_ratio(self) -> None:
        """Calculates the friction ratio (Rf) for the CPT data point.

        The friction ratio is calculated as the ratio of sleeve friction to cone resistance.
        If the sleeve friction is not available, the function returns None.
        If the cone resistance is zero, the function returns None.
        If the friction ratio is calculated, it is stored in the friction_ratio field.
        The friction ratio is expressed as a percentage.
        The formula for calculating the friction ratio is:
        Rf = (fs / qc) * 100
        where:
        - Rf is the friction ratio in percentage
        - fs is the sleeve friction in MPa
        - qc is the cone resistance in MPa
        """
        if self.cone_resistance is not None and self.cone_resistance != 0.0:
            if self.sleeve_friction is not None:
                self.friction_ratio = (
                    self.sleeve_friction / self.cone_resistance
                ) * 100.0

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the CPTLayer using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        for field in fields:
            if field == "depth":
                validate_field("depth", self.depth, 0.0, error_code_prefix="cpt")
            elif field == "cone_resistance":
                validate_field(
                    "cone_resistance",
                    self.cone_resistance,
                    0.0,
                    error_code_prefix="cpt",
                )
            elif field == "sleeve_friction":
                validate_field(
                    "sleeve_friction",
                    self.sleeve_friction,
                    0.0,
                    error_code_prefix="cpt",
                )
            elif field == "pore_pressure":
                validate_field(
                    "pore_pressure", self.pore_pressure, 0.0, error_code_prefix="cpt"
                )
            elif field == "friction_ratio":
                validate_field(
                    "friction_ratio", self.friction_ratio, 0.0, error_code_prefix="cpt"
                )
            else:
                raise ValidationError(
                    code="cpt.invalid_field",
                    message=f"Field '{field}' is not valid for CPT.",
                )


class CPTExp(BaseModel):
    """Represents a collection of CPT data points.

    A CPTExp struct contains multiple CPTLayer instances, forming a complete CPT profile.
    """

    layers: List[CPTLayer] = Field(default_factory=list)
    name: str = ""

    @classmethod
    def new(cls, layers: List[CPTLayer], name: str) -> "CPTExp":
        """Creates a new CPTExp instance.

        Args:
            layers: A list of CPTLayer instances
            name: The name of the CPT profile

        Returns:
            A new CPTExp instance
        """
        return cls(layers=layers, name=name)

    def add_layer(self, layer: CPTLayer) -> None:
        """Adds a new CPTLayer instance to the CPTExp collection.

        Args:
            layer: The CPTLayer instance to add to the collection
        """
        self.layers.append(layer)

    def get_layer_at_depth(self, depth: float) -> CPTLayer:
        """Retrieves the CPT layer corresponding to a given depth.

        This function finds the first layer whose depth is greater than or equal to the given depth.
        If no such layer is found, it returns the last layer in the list.

        Args:
            depth: The depth at which to search for a CPT layer

        Returns:
            The matching CPTLayer
        """
        for layer in self.layers:
            if layer.depth is not None and layer.depth >= depth:
                return layer
        return self.layers[-1] if self.layers else CPTLayer()

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the CPTExp using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.layers:
            raise ValidationError(
                code="cpt.empty_layers", message="No layers provided for CPTExp."
            )

        for layer in self.layers:
            layer.validate(fields)


class CPT(BaseModel):
    """Represents a collection of CPT tests.

    A CPT struct contains multiple CPTExp instances, each representing a single CPT profile.
    """

    exps: List[CPTExp] = Field(default_factory=list)
    idealization_method: SelectionMethod = SelectionMethod.AVG

    @classmethod
    def new(cls, exps: List[CPTExp], idealization_method: SelectionMethod) -> "CPT":
        """Creates a new CPT instance.

        Args:
            exps: A list of CPTExp instances
            idealization_method: The method used for idealization

        Returns:
            A new CPT instance
        """
        return cls(exps=exps, idealization_method=idealization_method)

    def add_exp(self, exp: CPTExp) -> None:
        """Adds a new CPTExp instance to the CPT collection.

        Args:
            exp: The CPTExp instance to add to the collection
        """
        self.exps.append(exp)

    def get_idealized_exp(self, name: str) -> CPTExp:
        """Creates an idealized CPT experiment based on the given mode.

        The idealized experiment is created by combining the corresponding layers from each
        individual experiment in the model.

        Args:
            name: The name of the idealized experiment

        Returns:
            A new CPTExp instance representing the idealized experiment
        """
        if not self.exps:
            return CPTExp.new([], name)

        mode = self.idealization_method

        # 1. Collect unique depths across all experiments
        unique_depths = set()
        for exp in self.exps:
            for layer in exp.layers:
                if layer.depth is not None:
                    unique_depths.add(layer.depth)

        sorted_depths = sorted(unique_depths)
        layers = []

        def get_mode_value(values: List[float]) -> float:
            if not values:
                return 0.0
            if mode == SelectionMethod.MIN:
                return min(values)
            elif mode == SelectionMethod.AVG:
                return sum(values) / len(values)
            else:  # MAX
                return max(values)

        for depth in sorted_depths:
            qc_at_depth = []
            fs_at_depth = []
            u2_at_depth = []

            for exp in self.exps:
                layer = exp.get_layer_at_depth(depth)
                if layer.cone_resistance is not None:
                    qc_at_depth.append(layer.cone_resistance)
                if layer.sleeve_friction is not None:
                    fs_at_depth.append(layer.sleeve_friction)
                if layer.pore_pressure is not None:
                    u2_at_depth.append(layer.pore_pressure)

            qc = get_mode_value(qc_at_depth)
            fs = get_mode_value(fs_at_depth)
            u2 = get_mode_value(u2_at_depth)

            layers.append(CPTLayer.new(depth, qc, fs, u2))

        return CPTExp.new(layers, name)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the CPT using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.exps:
            raise ValidationError(
                code="cpt.empty_exps", message="No experiments found in CPT."
            )

        for exp in self.exps:
            exp.validate(fields)
