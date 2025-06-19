# Development Guidelines

This document outlines the development practices, testing framework, and workflow for the QR Live Protocol (QRLP) project.

## 🚀 Quick Start with UV

### Prerequisites
- Python 3.8+
- [UV](https://docs.astral.sh/uv/) for dependency management
- Docker (optional, for containerized development)

### Setup
```bash
# Clone your fork
git clone https://github.com/your-username/qr_live_protocol.git
cd qrlp

# Install dependencies
uv sync

# Run development setup
./scripts/dev.sh dev-setup
```

## 🧪 Testing Framework

### Test Categories

We use a comprehensive testing pyramid with the following categories:

#### 1. **Unit Tests** (`@pytest.mark.unit`)
- **Location**: `tests/unit/`
- **Scope**: Individual functions/methods
- **Speed**: Fast (< 1 second)
- **Dependencies**: Mocked/isolated
- **Purpose**: Verify logic correctness

```bash
# Run unit tests
./scripts/dev.sh test-unit
# or
uv run pytest tests/unit/ -v
```

#### 2. **Integration Tests** (`@pytest.mark.integration`)
- **Location**: `tests/integration/`
- **Scope**: Component interactions
- **Speed**: Medium (1-10 seconds)
- **Dependencies**: Mocked external services
- **Purpose**: Verify components work together

```bash
# Run integration tests
./scripts/dev.sh test-integration
# or
uv run pytest tests/integration/ -v
```

#### 3. **System Tests** (`@pytest.mark.system`)
- **Location**: `tests/system/`
- **Scope**: Full system end-to-end
- **Speed**: Slow (10+ seconds)
- **Dependencies**: Real external services
- **Purpose**: Verify complete workflows

```bash
# Run system tests
./scripts/dev.sh test-system
# or
uv run pytest tests/system/ -v
```

#### 4. **Acceptance Tests** (`@pytest.mark.acceptance`)
- **Location**: `tests/acceptance/`
- **Scope**: User scenarios/features
- **Speed**: Variable
- **Dependencies**: Full system
- **Purpose**: Verify user requirements

```bash
# Run acceptance tests
uv run pytest tests/acceptance/ -v
```

#### 5. **Performance Tests** (`@pytest.mark.performance`)
- **Location**: `tests/performance/`
- **Scope**: System under load
- **Speed**: Very slow
- **Dependencies**: Full system
- **Purpose**: Verify performance requirements

```bash
# Run performance tests
uv run pytest tests/performance/ -v
```

#### 6. **Security Tests** (`@pytest.mark.security`)
- **Location**: `tests/security/`
- **Scope**: Security aspects
- **Speed**: Variable
- **Dependencies**: May need special tools
- **Purpose**: Verify security requirements

```bash
# Run security tests
uv run pytest tests/security/ -v
```

### Running Tests

```bash
# Run all tests
./scripts/dev.sh test

# Run with coverage
./scripts/dev.sh test-coverage

# Run specific test file
uv run pytest tests/unit/test_qr_data.py -v

# Run tests by marker
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run tests in parallel
uv run pytest -n auto

# Run with verbose output
uv run pytest -v
```

### Coverage Requirements
- **Minimum coverage**: 80%
- **Critical modules**: 90%+ (core.py, config.py)
- **New features**: Must include tests
- **Bug fixes**: Must include regression tests

## 🐳 Docker Development

### Docker Commands
```bash
# Build production image
./scripts/dev.sh docker-build

# Run production container
./scripts/dev.sh docker-run

# Run development container
./scripts/dev.sh docker-dev

# Run tests in container
./scripts/dev.sh docker-test
```

### Docker Compose
```bash
# Start development environment
docker-compose --profile dev up

# Start test environment
docker-compose --profile test up

# Start production environment
docker-compose up
```

## 🔄 Development Workflow

### 1. Setup Development Environment
```bash
# Install dependencies
./scripts/dev.sh install

# Run complete setup
./scripts/dev.sh dev-setup
```

### 2. Feature Development
```bash
# Create feature branch
git checkout -b feature/awesome-feature

# Make changes and test
./scripts/dev.sh test

# Format code
./scripts/dev.sh format

# Run linting
./scripts/dev.sh lint

# Commit with conventional format
git commit -m "feat: add awesome feature

- Added new QR style support
- Updated configuration options
- Added comprehensive tests

Fixes #123"
```

### 3. Testing Before PR
```bash
# Run full test suite
./scripts/dev.sh test

# Check coverage
./scripts/dev.sh test-coverage

# Run security checks
./scripts/dev.sh security

# Run type checking
./scripts/dev.sh type-check
```

## 🛠️ Quality Assurance

### Code Formatting
```bash
# Format code with Black and Ruff
./scripts/dev.sh format

# Check formatting
./scripts/dev.sh lint
```

### Type Checking
```bash
# Run MyPy type checking
./scripts/dev.sh type-check
```

### Security Scanning
```bash
# Run Bandit security checks
./scripts/dev.sh security
```

## 📊 CI/CD Integration

### GitHub Actions
Our CI/CD pipeline runs on every push and PR:

1. **Test Matrix**: Python 3.8-3.12
2. **Linting**: Black, Ruff, MyPy
3. **Security**: Bandit, Safety
4. **Integration**: End-to-end tests
5. **System**: Full system tests
6. **Docker**: Container building and testing
7. **Build**: Package building and validation

### Local vs CI Strategy
- **Local Development**: Use `uv run pytest` directly
- **CI/CD**: GitHub Actions for automated validation
- **Docker**: Consistent environment across local and CI

## 🎯 Cursor Rules

### Overview
We use `.cursor/rules` to provide AI assistance with consistent development practices. The rules cover:

- **Code Style**: PEP 8, type hints, dataclasses
- **Testing**: pytest patterns, mocking, coverage
- **Architecture**: Component design, patterns
- **Security**: Best practices, validation
- **Performance**: Caching, threading, monitoring

### Key Patterns

#### Configuration Management
```python
@dataclass
class QRLPConfig:
    update_interval: float = 5.0
    qr_settings: QRSettings = field(default_factory=QRSettings)
    # ... other settings
```

#### Context Managers
```python
def __enter__(self):
    self.start_live_generation()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self.stop_live_generation()
```

#### Callback System
```python
def add_update_callback(self, callback: Callable[[QRData, bytes], None]):
    self._callbacks.append(callback)
```

## 🐛 Debugging

### Debug Mode
```bash
# Enable debug logging
export QRLP_LOG_LEVEL=DEBUG
uv run python main.py

# Use debugger
import pdb; pdb.set_trace()
```

### Test Debugging
```bash
# Run single test with debug output
uv run pytest tests/unit/test_qr_data.py::TestQRData::test_qr_data_creation -v -s

# Run with print statements
uv run pytest -s

# Run with maximum verbosity
uv run pytest -vvv
```

### Docker Debugging
```bash
# Run container with debug mode
docker run -it -p 8080:8080 -e QRLP_LOG_LEVEL=DEBUG qrlp:latest

# Access container shell
docker run -it qrlp:latest /bin/bash
```

## 📚 Documentation

### Code Documentation
- **Google-style docstrings** for all public functions
- **Type hints** in function signatures
- **Examples** in docstrings
- **README updates** for user-facing changes

### API Documentation
- **API.md** for developer documentation
- **Examples** in examples/ directory
- **Configuration** examples in docs/

### Testing Documentation
- **Test docstrings** explaining test purpose
- **Fixture documentation** in conftest.py
- **Integration test** setup instructions

## 🔒 Security Guidelines

### Input Validation
```python
def validate_input(data: str) -> bool:
    """Validate user input before processing."""
    if not isinstance(data, str):
        return False
    if len(data) > MAX_INPUT_LENGTH:
        return False
    # Additional validation
    return True
```

### Secure Configuration
```python
# Use environment variables for secrets
api_key = os.getenv('QRLP_API_KEY')
if not api_key:
    raise ValueError("API key required")
```

### Error Handling
```python
try:
    result = external_api_call()
except ExternalAPIError as e:
    logger.error(f"API call failed: {e}")
    return None  # Graceful degradation
```

## 🚀 Performance Guidelines

### Caching
```python
@lru_cache(maxsize=128)
def expensive_operation(data: str) -> str:
    # Expensive computation
    return result
```

### Threading
```python
def start_background_task(self):
    thread = threading.Thread(target=self._background_work, daemon=True)
    thread.start()
```

### Resource Management
```python
def __enter__(self):
    self._setup_resources()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self._cleanup_resources()
```

## 📋 Checklist for Contributions

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Coverage is above 80%
- [ ] Documentation is updated
- [ ] Security checks pass
- [ ] Performance impact assessed
- [ ] Commit messages follow convention
- [ ] PR description is detailed

### For New Features
- [ ] Feature is well-documented
- [ ] Tests cover all code paths
- [ ] Configuration options added
- [ ] Examples provided
- [ ] Backward compatibility maintained

### For Bug Fixes
- [ ] Root cause identified
- [ ] Regression test added
- [ ] Fix is minimal and targeted
- [ ] Related issues checked
- [ ] Documentation updated if needed

## 🆘 Getting Help

### Resources
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Documentation**: Comprehensive guides in docs/
- **Examples**: Working examples in examples/

### Contact
- **Email**: contact@qrlp.org
- **GitHub**: @your-username
- **Discussions**: GitHub Discussions tab

---

This development guide ensures consistent quality and maintainability across the QRLP project. Follow these guidelines to contribute effectively and maintain high code standards. 