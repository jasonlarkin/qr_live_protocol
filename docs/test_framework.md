# Test Framework Documentation

## Overview

The QR Live Protocol project uses a comprehensive test framework built with pytest, organized into multiple categories to ensure thorough testing coverage across all components.

## Test Categories

### 🧪 Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Dependencies**: Minimal, often use mocks
- **Speed**: Fast execution
- **Examples**: QR data validation, configuration parsing

### 🔗 Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and interfaces
- **Scope**: Multiple components working together
- **Dependencies**: Real component interactions
- **Speed**: Medium execution
- **Examples**: QR generation with time provider, callback systems

### 🏗️ System Tests (`tests/system/`)
- **Purpose**: Test complete workflows and end-to-end scenarios
- **Scope**: Full system functionality
- **Dependencies**: Complete system stack
- **Speed**: Slower execution
- **Examples**: Complete QR generation workflow, live streaming

### 👥 Acceptance Tests (`tests/acceptance/`)
- **Purpose**: Test user scenarios and business requirements
- **Scope**: User-facing functionality
- **Dependencies**: User perspective validation
- **Speed**: Variable execution
- **Examples**: User can generate QR codes, verify authenticity

## Test Statistics

- **Total Tests**: 36
- **Unit Tests**: 5
- **Integration Tests**: 5
- **System Tests**: 3
- **Acceptance Tests**: 5
- **Core Tests**: 18

## Running Tests

### Local Development (Recommended)

```bash
# Install dependencies
uv sync

# Run all tests with coverage
uv run pytest

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m system        # System tests only
uv run pytest -m acceptance    # Acceptance tests only

# Run tests with verbose output
uv run pytest -v

# Run tests and generate coverage report
uv run pytest --cov=src --cov-report=html
```

### Docker Environment

```bash
# Run tests in Docker container
make test-docker

# Run specific test categories in Docker
docker-compose run --rm app uv run pytest -m unit
```

### CI/CD Pipeline

Tests are automatically run in GitHub Actions on:
- Pull requests
- Push to main branch
- Scheduled runs

## Test Configuration

### pytest.ini
- **Test Discovery**: `tests/` directory
- **Coverage**: 80% minimum threshold
- **Reports**: HTML, XML, and terminal output
- **Markers**: Custom markers for test categorization

### Coverage Configuration
- **Source**: `src/` directory
- **Threshold**: 80% minimum
- **Reports**: HTML (htmlcov/), XML, terminal

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_core.py             # Core functionality tests
├── unit/                    # Unit tests
│   ├── __init__.py
│   └── test_qr_data.py
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_core_integration.py
├── system/                  # System tests
│   ├── __init__.py
│   └── test_full_workflow.py
├── acceptance/              # Acceptance tests
│   ├── __init__.py
│   └── test_user_scenarios.py
├── performance/             # Performance tests (placeholder)
│   └── __init__.py
└── security/                # Security tests (placeholder)
    └── __init__.py
```

## Best Practices

### Writing Tests
1. **Use descriptive test names**: `test_user_can_generate_qr_code`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use appropriate markers**: `@pytest.mark.unit`
4. **Keep tests isolated**: No dependencies between tests
5. **Use fixtures for common setup**: Defined in `conftest.py`

### Test Organization
1. **Group related tests**: Use test classes
2. **Use meaningful file names**: `test_qr_data.py`
3. **Follow directory structure**: Match source code organization
4. **Include docstrings**: Explain test purpose

### Coverage Goals
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **System Tests**: Critical path coverage
- **Acceptance Tests**: User scenario coverage

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **Missing Dependencies**: Run `uv sync` to install
3. **Test Discovery**: Check `pytest.ini` configuration
4. **Coverage Issues**: Verify source paths in configuration

### Debugging Tests

```bash
# Run single test with debug output
uv run pytest tests/unit/test_qr_data.py::TestQRData::test_qr_data_creation -v -s

# Run tests with print statements
uv run pytest -s

# Run tests with detailed traceback
uv run pytest --tb=long
```

## Contributing

When adding new tests:

1. **Choose appropriate category**: Unit, integration, system, or acceptance
2. **Use existing patterns**: Follow established test structure
3. **Add markers**: Use `@pytest.mark.category` decorators
4. **Update documentation**: Add test descriptions if needed
5. **Ensure coverage**: Maintain minimum coverage thresholds

## Future Enhancements

- [ ] Performance test suite
- [ ] Security test suite
- [ ] Load testing for live generation
- [ ] Browser automation for web interface
- [ ] API contract testing
- [ ] Mutation testing for robustness 