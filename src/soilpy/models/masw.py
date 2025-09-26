"""MASW (Multichannel Analysis of Surface Waves) model for SoilPy."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ..enums import SelectionMethod
from ..validation import ValidationError, validate_field


class MaswLayer(BaseModel):
    """Represents an individual MASW (Multichannel Analysis of Surface Waves) experiment layer.

    Attributes:
        thickness: The thickness of the layer in meters
        vs: The shear wave velocity of the layer in meters per second
        vp: The compressional wave velocity of the layer in meters per second
        depth: The depth of the layer in meters
    """

    thickness: Optional[float] = None
    vs: Optional[float] = None
    vp: Optional[float] = None
    depth: Optional[float] = None

    @classmethod
    def new(cls, thickness: float, vs: float, vp: float) -> "MaswLayer":
        """Creates a new MaswLayer instance.

        Args:
            thickness: The thickness of the layer in meters
            vs: The shear wave velocity of the layer in meters per second
            vp: The compressional wave velocity of the layer in meters per second

        Returns:
            A new MaswLayer instance
        """
        return cls(thickness=thickness, vs=vs, vp=vp, depth=None)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the MaswLayer using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        for field in fields:
            if field == "depth":
                validate_field("depth", self.depth, 0.0, error_code_prefix="masw")
            elif field == "thickness":
                validate_field(
                    "thickness", self.thickness, 0.0001, error_code_prefix="masw"
                )
            elif field == "vs":
                validate_field("vs", self.vs, 0.0, error_code_prefix="masw")
            elif field == "vp":
                validate_field("vp", self.vp, 0.0, error_code_prefix="masw")
            else:
                raise ValidationError(
                    code="masw.invalid_field",
                    message=f"Field '{field}' is not valid for MASW.",
                )


class MaswExp(BaseModel):
    """Represents a MASW (Multichannel Analysis of Surface Waves) experiment.

    Attributes:
        layers: A list of MaswLayer instances representing the individual layers of the experiment
        name: The name of the experiment
    """

    layers: List[MaswLayer] = Field(default_factory=list)
    name: str = ""

    @classmethod
    def new(cls, layers: List[MaswLayer], name: str) -> "MaswExp":
        """Creates a new MaswExp instance.

        Args:
            layers: A list of MaswLayer instances
            name: The name of the experiment

        Returns:
            A new MaswExp instance with calculated depths
        """
        instance = cls(layers=layers, name=name)
        instance.calc_depths()
        return instance

    def calc_depths(self) -> None:
        """Calculates and updates the depth of each MASW experiment layer.

        Depth is calculated as a cumulative sum of layer thicknesses.
        - The first layer's depth is equal to its thickness.
        - Each subsequent layer's depth is the sum of all previous layers' thicknesses.

        Raises:
            ValueError: If any layer has a thickness value of 0.0 or less
        """
        if not self.layers:
            return

        bottom = 0.0

        for layer in self.layers:
            if layer.thickness is None:
                raise ValueError("Layer thickness must be set")

            if layer.thickness <= 0.0:
                raise ValueError(
                    "Thickness of MASW experiment must be greater than zero."
                )

            layer.depth = bottom + layer.thickness
            bottom += layer.thickness

    def get_layer_at_depth(self, depth: float) -> MaswLayer:
        """Retrieves the MASW experiment layer corresponding to a given depth.

        This function finds the first layer whose depth is greater than or equal to the given depth.
        If no such layer is found, it returns the last layer in the list.

        Args:
            depth: The depth at which to search for an experiment layer

        Returns:
            The matching MaswLayer
        """
        for layer in self.layers:
            if layer.depth is not None and layer.depth >= depth:
                return layer
        return self.layers[-1] if self.layers else MaswLayer()

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the MaswExp using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.layers:
            raise ValidationError(
                code="masw.empty_layers", message="No layers provided for MaswExp."
            )

        for layer in self.layers:
            layer.validate(fields)


class Masw(BaseModel):
    """Represents a MASW (Multichannel Analysis of Surface Waves) model.

    Attributes:
        exps: A list of MaswExp instances representing the individual experiments in the model
        idealization_method: The method used for idealization
    """

    exps: List[MaswExp] = Field(default_factory=list)
    idealization_method: SelectionMethod = SelectionMethod.AVG

    @classmethod
    def new(cls, exps: List[MaswExp], idealization_method: SelectionMethod) -> "Masw":
        """Creates a new Masw instance.

        Args:
            exps: A list of MaswExp instances
            idealization_method: The method used for idealization

        Returns:
            A new Masw instance with calculated depths
        """
        for exp in exps:
            exp.calc_depths()
        return cls(exps=exps, idealization_method=idealization_method)

    def add_exp(self, exp: MaswExp) -> None:
        """Adds a new MaswExp instance to the Masw collection.

        Args:
            exp: The MaswExp instance to add to the collection
        """
        self.exps.append(exp)

    def calc_depths(self) -> None:
        """Calculates and updates the depth of each MASW experiment layer in the model."""
        for exp in self.exps:
            exp.calc_depths()

    def get_idealized_exp(self, name: str) -> MaswExp:
        """Creates an idealized MASW experiment based on the given mode.

        The idealized experiment is created by combining the corresponding layers from each
        individual experiment in the model.

        Args:
            name: The name of the idealized experiment

        Returns:
            A new MaswExp instance representing the idealized experiment
        """
        if not self.exps:
            return MaswExp.new([], name)

        mode = self.idealization_method
        self.calc_depths()

        # 1. Collect unique depths across all experiments
        unique_depths = {0.0}  # Add the surface depth
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

        for i in range(len(sorted_depths) - 1):
            top = sorted_depths[i]
            bottom = sorted_depths[i + 1]
            thickness = bottom - top

            vs_at_depth = []
            vp_at_depth = []

            for exp in self.exps:
                layer = exp.get_layer_at_depth((top + bottom) / 2.0)
                if layer.vs is not None:
                    vs_at_depth.append(layer.vs)
                if layer.vp is not None:
                    vp_at_depth.append(layer.vp)

            vs = get_mode_value(vs_at_depth)
            vp = get_mode_value(vp_at_depth)

            layers.append(MaswLayer.new(thickness, vs, vp))

        return MaswExp.new(layers, name)

    def validate(self, fields: List[str]) -> None:
        """Validates specific fields of the Masw using field names.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any field is invalid
        """
        if not self.exps:
            raise ValidationError(
                code="masw.empty_exps", message="No experiments provided for Masw."
            )

        for exp in self.exps:
            exp.validate(fields)
