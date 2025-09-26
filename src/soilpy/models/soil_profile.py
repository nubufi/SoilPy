"""Soil profile model for SoilPy."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ..validation import ValidationError, validate_field


class SoilLayer(BaseModel):
    """Represents a single soil layer in a geotechnical engineering model.

    This class contains essential soil properties used for analysis, such as
    shear strength, stiffness, and classification parameters. The parameters are
    divided into **total stress** (undrained) and **effective stress** (drained)
    conditions for comprehensive modeling.
    """

    soil_classification: Optional[str] = None  # e.g., "CLAY", "SAND", "SILT"
    thickness: Optional[float] = None  # meter
    natural_unit_weight: Optional[float] = None  # t/m³
    dry_unit_weight: Optional[float] = None  # t/m³
    saturated_unit_weight: Optional[float] = None  # t/m³
    depth: Optional[float] = None  # meter
    center: Optional[float] = None  # meter
    damping_ratio: Optional[float] = None  # percentage
    fine_content: Optional[float] = None  # percentage
    liquid_limit: Optional[float] = None  # percentage
    plastic_limit: Optional[float] = None  # percentage
    plasticity_index: Optional[float] = None  # percentage
    cu: Optional[float] = None  # Undrained shear strength in t/m²
    c_prime: Optional[float] = None  # Effective cohesion in t/m²
    phi_u: Optional[float] = None  # Undrained internal friction angle in degrees
    phi_prime: Optional[float] = None  # Effective internal friction angle in degrees
    water_content: Optional[float] = None  # percentage
    poissons_ratio: Optional[float] = None  # Poisson's ratio
    elastic_modulus: Optional[float] = None  # t/m²
    void_ratio: Optional[float] = None  # Void ratio
    recompression_index: Optional[float] = None  # Recompression index
    compression_index: Optional[float] = None  # Compression index
    preconsolidation_pressure: Optional[float] = None  # t/m²
    mv: Optional[float] = None  # volume compressibility coefficient in m²/t
    shear_wave_velocity: Optional[float] = None  # m/s

    @classmethod
    def new(cls, thickness: float) -> "SoilLayer":
        """Creates a new SoilLayer with specified thickness.

        Args:
            thickness: Thickness of the soil layer in meters

        Returns:
            A new SoilLayer instance
        """
        return cls(thickness=thickness)

    def validate_fields(self, fields: List[str]) -> None:
        """Validate based on a list of required fields by name.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If any required field is invalid
        """
        for field in fields:
            if field == "thickness":
                validate_field(
                    "thickness",
                    self.thickness,
                    0.0001,
                    error_code_prefix="soil_profile",
                )
            elif field == "natural_unit_weight":
                validate_field(
                    "natural_unit_weight",
                    self.natural_unit_weight,
                    0.1,
                    10.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "dry_unit_weight":
                validate_field(
                    "dry_unit_weight",
                    self.dry_unit_weight,
                    0.1,
                    10.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "saturated_unit_weight":
                validate_field(
                    "saturated_unit_weight",
                    self.saturated_unit_weight,
                    0.1,
                    10.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "damping_ratio":
                validate_field(
                    "damping_ratio",
                    self.damping_ratio,
                    0.1,
                    100.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "fine_content":
                validate_field(
                    "fine_content",
                    self.fine_content,
                    0.0,
                    100.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "liquid_limit":
                validate_field(
                    "liquid_limit",
                    self.liquid_limit,
                    0.0,
                    100.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "plastic_limit":
                validate_field(
                    "plastic_limit",
                    self.plastic_limit,
                    0.0,
                    100.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "plasticity_index":
                validate_field(
                    "plasticity_index",
                    self.plasticity_index,
                    0.0,
                    100.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "cu":
                validate_field("cu", self.cu, 0.0, error_code_prefix="soil_profile")
            elif field == "c_prime":
                validate_field(
                    "c_prime", self.c_prime, 0.0, error_code_prefix="soil_profile"
                )
            elif field == "phi_u":
                validate_field(
                    "phi_u", self.phi_u, 0.0, 90.0, error_code_prefix="soil_profile"
                )
            elif field == "phi_prime":
                validate_field(
                    "phi_prime",
                    self.phi_prime,
                    0.0,
                    90.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "water_content":
                validate_field(
                    "water_content",
                    self.water_content,
                    0.0,
                    100.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "poissons_ratio":
                validate_field(
                    "poissons_ratio",
                    self.poissons_ratio,
                    0.0001,
                    0.5,
                    error_code_prefix="soil_profile",
                )
            elif field == "elastic_modulus":
                validate_field(
                    "elastic_modulus",
                    self.elastic_modulus,
                    0.0001,
                    error_code_prefix="soil_profile",
                )
            elif field == "void_ratio":
                validate_field(
                    "void_ratio", self.void_ratio, 0.0, error_code_prefix="soil_profile"
                )
            elif field == "compression_index":
                validate_field(
                    "compression_index",
                    self.compression_index,
                    0.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "recompression_index":
                validate_field(
                    "recompression_index",
                    self.recompression_index,
                    0.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "preconsolidation_pressure":
                validate_field(
                    "preconsolidation_pressure",
                    self.preconsolidation_pressure,
                    0.0,
                    error_code_prefix="soil_profile",
                )
            elif field == "mv":
                validate_field("mv", self.mv, 0.0, error_code_prefix="soil_profile")
            elif field == "shear_wave_velocity":
                validate_field(
                    "shear_wave_velocity",
                    self.shear_wave_velocity,
                    0.0,
                    error_code_prefix="soil_profile",
                )
            else:
                raise ValidationError(
                    code="soil_profile.invalid_field",
                    message=f"Field '{field}' is not valid for SoilLayer.",
                )


class SoilProfile(BaseModel):
    """Represents a soil profile consisting of multiple soil layers.

    This structure stores soil layers and calculates normal and effective stresses.
    """

    layers: List[SoilLayer] = Field(default_factory=list)
    ground_water_level: Optional[float] = None  # meters

    def model_post_init(self, __context) -> None:
        """Initialize layer depths after object creation."""
        if self.layers:
            self.calc_layer_depths()

    @classmethod
    def new(cls, layers: List[SoilLayer], ground_water_level: float) -> "SoilProfile":
        """Creates a new soil profile and initializes layer depths.

        Args:
            layers: A list of SoilLayer objects
            ground_water_level: Depth of the groundwater table in meters

        Returns:
            A new SoilProfile instance

        Raises:
            ValueError: If no layers are provided
        """
        if not layers:
            raise ValueError("Soil profile must contain at least one layer.")

        profile = cls(layers=layers, ground_water_level=ground_water_level)
        profile.calc_layer_depths()
        return profile

    def calc_layer_depths(self) -> None:
        """Calculates center and bottom depth for each soil layer."""
        if not self.layers:
            return

        bottom = 0.0

        for layer in self.layers:
            if layer.thickness is None:
                raise ValueError("Layer thickness must be set")

            layer.center = bottom + layer.thickness / 2.0
            bottom += layer.thickness
            layer.depth = bottom

    def get_layer_index(self, depth: float) -> int:
        """Returns the index of the soil layer at a specified depth.

        Args:
            depth: The depth at which to find the layer

        Returns:
            The index of the layer containing the specified depth
        """
        for i, layer in enumerate(self.layers):
            if layer.depth is not None and layer.depth >= depth:
                return i
        return len(self.layers) - 1

    def get_layer_at_depth(self, depth: float) -> SoilLayer:
        """Returns a reference to the soil layer at a specified depth.

        Args:
            depth: The depth at which to find the layer

        Returns:
            The SoilLayer at the specified depth
        """
        index = self.get_layer_index(depth)
        return self.layers[index]

    def calc_normal_stress(self, depth: float) -> float:
        """Calculates the total (normal) stress at a given depth.

        Args:
            depth: The depth at which to calculate total stress

        Returns:
            The total normal stress (t/m²) at the specified depth
        """
        if self.ground_water_level is None:
            raise ValueError("Ground water level must be set")

        layer_index = self.get_layer_index(depth)
        total_stress = 0.0
        previous_depth = 0.0
        gwt = self.ground_water_level

        for i, layer in enumerate(self.layers[: layer_index + 1]):
            if layer.thickness is None:
                raise ValueError("Layer thickness must be set")

            layer_thickness = (
                depth - previous_depth if i == layer_index else layer.thickness
            )

            dry_unit_weight = layer.dry_unit_weight or 0.0
            saturated_unit_weight = layer.saturated_unit_weight or 0.0

            if dry_unit_weight <= 1.0 and saturated_unit_weight <= 1.0:
                raise ValueError(
                    "Dry or saturated unit weight must be greater than 1 for each layer."
                )

            if gwt >= previous_depth + layer_thickness:
                # Entirely above groundwater table (dry unit weight applies)
                total_stress += dry_unit_weight * layer_thickness
            elif gwt <= previous_depth:
                # Entirely below groundwater table (saturated unit weight applies)
                total_stress += saturated_unit_weight * layer_thickness
            else:
                # Partially submerged (both dry and saturated weights apply)
                dry_thickness = gwt - previous_depth
                submerged_thickness = layer_thickness - dry_thickness
                total_stress += (
                    dry_unit_weight * dry_thickness
                    + saturated_unit_weight * submerged_thickness
                )

            previous_depth += layer_thickness

        return total_stress

    def calc_effective_stress(self, depth: float) -> float:
        """Calculates the effective stress at a given depth.

        Args:
            depth: The depth at which to calculate effective stress

        Returns:
            The effective stress (t/m²) at the specified depth
        """
        if self.ground_water_level is None:
            raise ValueError("Ground water level must be set")

        normal_stress = self.calc_normal_stress(depth)

        if self.ground_water_level >= depth:
            return (
                normal_stress  # Effective stress equals total stress above water table
            )
        else:
            pore_pressure = (depth - self.ground_water_level) * 0.981  # t/m³ for water
            return normal_stress - pore_pressure

    def validate(self, fields: List[str]) -> None:
        """Validates the soil profile and its layers.

        Args:
            fields: A list of field names to validate

        Raises:
            ValidationError: If the profile is invalid
        """
        if not self.layers:
            raise ValidationError(
                code="soil_profile.empty",
                message="Soil profile must contain at least one layer.",
            )

        for layer in self.layers:
            layer.validate_fields(fields)

        validate_field(
            "ground_water_level",
            self.ground_water_level,
            0.0,
            error_code_prefix="soil_profile",
        )
