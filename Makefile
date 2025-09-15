# Makefile for DAI Continuous Testing Utilities Collection

.PHONY: test test-unit test-integration test-all check validate coverage lint clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-all      - Run all tests with full validation"
	@echo "  check         - Run validation checks only"
	@echo "  validate      - Validate module structure"
	@echo "  coverage      - Check test coverage"
	@echo "  lint          - Run linting checks"
	@echo "  clean         - Clean up test artifacts"
	@echo "  install-dev   - Install development dependencies"

# Test targets
test:
	python tests/run_tests.py

test-unit:
	python tests/run_tests.py --type unit

test-integration:
	python tests/run_tests.py --type integration

test-all:
	python tests/run_tests.py --all-checks --verbose

# Validation targets
check: validate coverage lint

validate:
	python tests/run_tests.py --validate

coverage:
	python tests/run_tests.py --coverage

lint:
	python tests/run_tests.py --lint

# Utility targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.backup*" -delete
	find . -type f -name "*.tmp" -delete

install-dev:
	@echo "Installing development dependencies..."
	@echo "This collection uses only Python standard library modules."
	@echo "No additional dependencies required for testing."

# CI/CD target
ci: clean test-all
	@echo "CI/CD pipeline completed successfully"

# Quick check for development
dev-check: validate lint test-unit
	@echo "Development checks completed"
