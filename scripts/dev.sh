#!/bin/bash

# QRLP Development Scripts
# Usage: ./scripts/dev.sh [command]

set -e

case "$1" in
    "install")
        echo "Installing dependencies with uv..."
        uv sync
        ;;
    "test")
        echo "Running tests..."
        uv run pytest
        ;;
    "test-unit")
        echo "Running unit tests..."
        uv run pytest tests/unit/ -v
        ;;
    "test-integration")
        echo "Running integration tests..."
        uv run pytest tests/integration/ -v
        ;;
    "test-system")
        echo "Running system tests..."
        uv run pytest tests/system/ -v
        ;;
    "test-coverage")
        echo "Running tests with coverage..."
        uv run pytest --cov=src --cov-report=html --cov-report=term-missing
        ;;
    "lint")
        echo "Running linting..."
        uv run black --check src/ tests/
        uv run ruff check src/ tests/
        ;;
    "format")
        echo "Formatting code..."
        uv run black src/ tests/
        uv run ruff check --fix src/ tests/
        ;;
    "type-check")
        echo "Running type checking..."
        uv run mypy src/
        ;;
    "security")
        echo "Running security checks..."
        uv run bandit -r src/
        uv run safety check
        ;;
    "dev-setup")
        echo "Setting up development environment..."
        uv sync
        uv run black src/ tests/
        uv run pytest
        ;;
    "demo")
        echo "Running QRLP demo..."
        uv run python main.py
        ;;
    "docker-build")
        echo "Building Docker image..."
        docker build -t qrlp:latest .
        ;;
    "docker-run")
        echo "Running QRLP in Docker..."
        docker run -p 8080:8080 qrlp:latest
        ;;
    "docker-dev")
        echo "Running QRLP in development Docker..."
        docker-compose --profile dev up qrlp-dev
        ;;
    "docker-test")
        echo "Running tests in Docker..."
        docker-compose --profile test up qrlp-test
        ;;
    *)
        echo "Usage: $0 {install|test|test-unit|test-integration|test-system|test-coverage|lint|format|type-check|security|dev-setup|demo|docker-build|docker-run|docker-dev|docker-test}"
        echo ""
        echo "Commands:"
        echo "  install        - Install dependencies"
        echo "  test           - Run all tests"
        echo "  test-unit      - Run unit tests only"
        echo "  test-integration - Run integration tests only"
        echo "  test-system    - Run system tests only"
        echo "  test-coverage  - Run tests with coverage report"
        echo "  lint           - Run linting checks"
        echo "  format         - Format code"
        echo "  type-check     - Run type checking"
        echo "  security       - Run security checks"
        echo "  dev-setup      - Complete development setup"
        echo "  demo           - Run QRLP demo"
        echo "  docker-build   - Build Docker image"
        echo "  docker-run     - Run QRLP in Docker"
        echo "  docker-dev     - Run development Docker"
        echo "  docker-test    - Run tests in Docker"
        exit 1
        ;;
esac 