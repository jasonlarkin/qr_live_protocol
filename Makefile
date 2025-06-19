.PHONY: help install test test-unit test-integration test-coverage lint format type-check security clean build

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  security     - Run security checks"
	@echo "  clean        - Clean up generated files"
	@echo "  build        - Build package"
	@echo "  dev-setup    - Complete development setup"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Run all tests
test:
	pytest

# Run unit tests only
test-unit:
	pytest -m "not integration and not slow"

# Run integration tests only
test-integration:
	pytest -m integration

# Run tests with coverage
test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Run linting
lint:
	flake8 src/ tests/
	black --check src/ tests/

# Format code
format:
	black src/ tests/

# Type checking
type-check:
	mypy src/

# Security checks
security:
	bandit -r src/
	safety check

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build package
build:
	python -m build

# Complete development setup
dev-setup: install format lint type-check test

# Quick development cycle
dev: format lint test

# Run demo
demo:
	python main.py

# Run with specific port
demo-port:
	python main.py --port 8081

# Run without browser
demo-no-browser:
	python main.py --no-browser 