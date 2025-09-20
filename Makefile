# Makefile for SoilPy project
# Usage: make test, make setup, make clean, etc.

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help test test-verbose test-quick test-failed setup clean install lint format status

help: ## Show this help message
	@echo "Available targets:"
	@echo "  test          - Run Python tests for SoilPy"
	@echo "  test-verbose  - Run tests with verbose output"
	@echo "  test-quick    - Run tests quickly (no verbose output)"
	@echo "  test-failed   - Run only failed tests"
	@echo "  setup         - Setup Python virtual environment and dependencies"
	@echo "  install       - Install SoilPy in development mode"
	@echo "  lint          - Run linting on SoilPy code"
	@echo "  format        - Format SoilPy code"
	@echo "  clean         - Clean build artifacts"
	@echo "  status        - Check project status"
	@echo ""
	@echo "Usage examples:"
	@echo "  make test                    # Run all tests"
	@echo "  make test-verbose            # Run tests with verbose output"
	@echo "  make setup                   # Setup environment"

test: ## Run Python tests for SoilPy
	@echo "$(GREEN)Running SoilPy tests...$(NC)"
	@if [ ! -d "venv" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		python3 -m venv venv; \
	fi && \
	source venv/bin/activate && \
	pip install -e . && \
	PYTHONPATH=src python -m pytest tests/ -v --tb=short

test-verbose: ## Run SoilPy tests with verbose output
	@echo "$(GREEN)Running SoilPy tests (verbose)...$(NC)"
	@source venv/bin/activate && \
	PYTHONPATH=src python -m pytest tests/ -v -s --tb=long

test-quick: ## Run SoilPy tests quickly (no verbose output)
	@echo "$(GREEN)Running SoilPy tests (quick)...$(NC)"
	@source venv/bin/activate && \
	PYTHONPATH=src python -m pytest tests/ --tb=no -q

test-failed: ## Run only failed SoilPy tests
	@echo "$(GREEN)Running failed SoilPy tests...$(NC)"
	@source venv/bin/activate && \
	PYTHONPATH=src python -m pytest tests/ --lf -v

setup: ## Setup Python virtual environment and dependencies
	@echo "$(YELLOW)Setting up SoilPy environment...$(NC)"
	@python3 -m venv venv && \
	source venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -e . && \
	pip install -e ".[dev]"

install: ## Install SoilPy in development mode
	@echo "$(YELLOW)Installing SoilPy in development mode...$(NC)"
	@source venv/bin/activate && \
	pip install -e .

lint: ## Run linting on SoilPy code
	@echo "$(YELLOW)Running linting on SoilPy...$(NC)"
	@source venv/bin/activate && \
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

format: ## Format SoilPy code
	@echo "$(YELLOW)Formatting SoilPy code...$(NC)"
	@source venv/bin/activate && \
	black src/ tests/ --line-length=100

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@rm -rf venv/ __pycache__/ .pytest_cache/ src/*/__pycache__/ src/*/*/__pycache__/ .coverage htmlcov/ dist/ build/ *.egg-info/

status: ## Check project status
	@echo "$(BLUE)Checking SoilPy project status...$(NC)"
	@if [ -d "venv" ]; then \
		echo "$(GREEN)Virtual environment: ✓$(NC)"; \
	else \
		echo "$(RED)Virtual environment: ✗$(NC)"; \
	fi
	@if [ -f "pyproject.toml" ]; then \
		echo "$(GREEN)Project configuration: ✓$(NC)"; \
	else \
		echo "$(RED)Project configuration: ✗$(NC)"; \
	fi
	@if [ -d "src/soilpy" ]; then \
		echo "$(GREEN)Source code: ✓$(NC)"; \
	else \
		echo "$(RED)Source code: ✗$(NC)"; \
	fi
	@if [ -d "tests" ]; then \
		echo "$(GREEN)Tests: ✓$(NC)"; \
	else \
		echo "$(RED)Tests: ✗$(NC)"; \
	fi

# Development helpers
dev-install: setup ## Setup development environment (alias for setup)
	@echo "$(GREEN)Development environment ready!$(NC)"

check: lint ## Run code quality checks (alias for lint)
	@echo "$(GREEN)Code quality checks completed!$(NC)"

# Test specific modules
test-models: ## Run tests for models only
	@echo "$(GREEN)Running model tests...$(NC)"
	@source venv/bin/activate && \
	PYTHONPATH=src python -m pytest tests/test_*.py -v

test-calculations: ## Run tests for calculation modules only
	@echo "$(GREEN)Running calculation tests...$(NC)"
	@source venv/bin/activate && \
	PYTHONPATH=src python -m pytest tests/test_*bearing* tests/test_*settlement* tests/test_*liquefaction* -v

# Coverage
coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@source venv/bin/activate && \
	pip install coverage && \
	PYTHONPATH=src coverage run -m pytest tests/ && \
	coverage report && \
	coverage html

# Documentation
docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	@source venv/bin/activate && \
	pip install sphinx sphinx-rtd-theme && \
	sphinx-build -b html docs/ docs/_build/html

# Package management
build: ## Build package
	@echo "$(GREEN)Building SoilPy package...$(NC)"
	@source venv/bin/activate && \
	python -m build

publish: ## Publish package to PyPI (requires credentials)
	@echo "$(GREEN)Publishing SoilPy package...$(NC)"
	@source venv/bin/activate && \
	python -m twine upload dist/*