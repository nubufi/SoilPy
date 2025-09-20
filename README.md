# SoilPy

A comprehensive geotechnical engineering library for soil mechanics calculations in Python. SoilPy provides a wide range of tools for foundation design, soil analysis, and geotechnical calculations used in civil engineering practice.

## 🚀 Features

### Foundation Analysis
- **Bearing Capacity Analysis**: Multiple methods including Vesic, Tezcan-Ozdemir, and Point Load Test
- **Settlement Analysis**: Elastic settlement (Boussinesq) and consolidation settlement (compression index and Mv methods)
- **Foundation Design**: Effective depth calculations and horizontal sliding analysis
- **Load Analysis**: Comprehensive load modeling with eccentricity calculations

### Soil Classification & Analysis
- **Local Soil Classification**: Based on Cu (undrained shear strength), SPT (Standard Penetration Test), and VS (shear wave velocity)
- **Soil Profile Management**: Comprehensive soil layer modeling with stress calculations
- **Swelling Potential**: Kayabalu & Yaldız (2014) method for expansive soil analysis

### Liquefaction Assessment
- **SPT-based Methods**: Seed-Idriss method for liquefaction potential evaluation
- **VS-based Methods**: Andrus-Stokoe method using shear wave velocity
- **Settlement Calculations**: Post-liquefaction settlement estimates

### Laboratory & Field Testing
- **SPT Analysis**: Standard Penetration Test data processing with corrections
- **CPT Analysis**: Cone Penetration Test data handling and interpretation
- **MASW Analysis**: Multichannel Analysis of Surface Waves data processing
- **Point Load Test**: Rock strength analysis and bearing capacity calculations

## 📦 Installation

### From PyPI (when available)
```bash
pip install soilpy
```

### From Source
```bash
git clone https://github.com/your-username/soilpy.git
cd soilpy
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/your-username/soilpy.git
cd soilpy
make setup  # Sets up virtual environment and installs dependencies
```

## 🏃‍♂️ Quick Start

### Basic Foundation Analysis
```python
from soilpy.models import Foundation, SoilLayer, SoilProfile, Loads
from soilpy.bearing_capacity.vesic import calc_bearing_capacity

# Create a foundation
foundation = Foundation(
    foundation_depth=2.0,
    foundation_length=10.0,
    foundation_width=5.0
)

# Create soil layers
layers = [
    SoilLayer(
        thickness=2.0,
        dry_unit_weight=1.8,
        saturated_unit_weight=2.0,
        cu=50.0,
        phi_prime=30.0
    )
]

# Create soil profile
profile = SoilProfile(layers=layers, ground_water_level=1.5)

# Calculate bearing capacity
capacity = calc_bearing_capacity(foundation, profile, 100.0)  # 100 t/m² pressure
print(f"Bearing capacity: {capacity.ultimate_bearing_capacity} t/m²")
```

### Settlement Analysis
```python
from soilpy.elastic_settlement.boussinesq import calc_elastic_settlement

# Calculate elastic settlement
settlement_result = calc_elastic_settlement(profile, foundation, 100.0)
print(f"Total settlement: {settlement_result.total_settlement} cm")
```

### SPT Data Analysis
```python
from soilpy.models.spt import NValue, SPT, SPTExp, SPTBlow
from soilpy.enums import SelectionMethod

# Create SPT data
spt_exp = SPTExp.new([], "Borehole-1")
spt_exp.add_blow(1.5, NValue(15))
spt_exp.add_blow(3.0, NValue(25))
spt_exp.add_blow(4.5, NValue(30))

# Create SPT collection
spt = SPT.new(1.2, 1.05, 0.9, SelectionMethod.AVG)
spt.add_exp(spt_exp)

# Get idealized experiment
idealized = spt.get_idealized_exp("Idealized")
print(f"Number of blows: {len(idealized.blows)}")
```

## 🛠️ Development

### Setup Development Environment
```bash
make setup          # Setup virtual environment and install dependencies
make test           # Run all tests
make test-verbose   # Run tests with verbose output
make lint           # Run code linting
make format         # Format code with black
```

### Available Make Commands
- `make test` - Run all tests
- `make test-verbose` - Run tests with verbose output
- `make test-quick` - Run tests quickly
- `make test-failed` - Run only failed tests
- `make setup` - Setup development environment
- `make clean` - Clean build artifacts
- `make lint` - Run code linting
- `make format` - Format code
- `make coverage` - Run tests with coverage report
- `make status` - Check project status

### Running Tests
```bash
# Run all tests
make test

# Run specific test modules
make test-models
make test-calculations

# Run with coverage
make coverage
```

## 📚 Documentation

### API Reference
- **Models**: Foundation, SoilProfile, SoilLayer, Loads, SPT, CPT, MASW
- **Bearing Capacity**: Vesic, Tezcan-Ozdemir, Point Load Test methods
- **Settlement**: Elastic (Boussinesq), Consolidation (Cc-Cr, Mv methods)
- **Liquefaction**: SPT-based (Seed-Idriss), VS-based (Andrus-Stokoe)
- **Soil Classification**: Local soil classification by Cu, SPT, VS

### Examples
See the `tests/` directory for comprehensive examples of all functionality.

## 🧪 Testing

The library includes comprehensive tests covering all major functionality:

```bash
# Run all tests (117 test cases)
make test

# Run specific test categories
make test-models        # Model tests
make test-calculations  # Calculation tests
```

Test coverage includes:
- ✅ Bearing capacity calculations (Vesic, Tezcan-Ozdemir, Point Load Test)
- ✅ Settlement analysis (Elastic, Consolidation)
- ✅ Liquefaction assessment (SPT, VS methods)
- ✅ Soil classification (Cu, SPT, VS)
- ✅ Foundation design (Effective depth, Horizontal sliding)
- ✅ Laboratory testing (SPT, CPT, MASW, Point Load Test)
- ✅ Swelling potential analysis

## 📋 Requirements

- Python 3.8+
- NumPy
- SciPy (for some advanced calculations)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`make test`)
6. Run linting (`make lint`)
7. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all public functions
- Include comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Vesic Method**: Based on Vesic (1973) bearing capacity theory
- **Tezcan-Ozdemir Method**: Based on Tezcan & Ozdemir (2004) approach
- **Seed-Idriss Method**: Based on Seed & Idriss (1971) liquefaction assessment
- **Andrus-Stokoe Method**: Based on Andrus & Stokoe (2000) VS-based liquefaction
- **Kayabalu & Yaldız Method**: Based on Kayabalu & Yaldız (2014) swelling potential

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation
- Review the test examples

---

**SoilPy** - Making geotechnical engineering calculations accessible and reliable in Python.