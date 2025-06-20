"""
Pytest configuration and fixtures for QRLP tests.

This file contains shared fixtures and configuration that can be used
across all test files in the project.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add src to path for imports
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import QRLPConfig, QRSettings, TimeSettings, BlockchainSettings
from src.core import QRLiveProtocol, QRData


@pytest.fixture
def sample_config() -> QRLPConfig:
    """Provide a sample configuration for testing."""
    config = QRLPConfig()
    config.update_interval = 1.0
    config.web_settings.port = 8081  # Use different port for testing
    config.blockchain_settings.enabled_chains = {"bitcoin"}
    config.time_settings.timeout = 1.0  # Faster timeouts for tests
    return config


@pytest.fixture
def mock_time_provider():
    """Mock time provider that returns predictable values."""
    with patch("src.time_provider.TimeProvider") as mock:
        provider = mock.return_value
        provider.get_current_time.return_value = "2025-01-11T12:00:00.000Z"
        provider.get_time_server_verification.return_value = {"pool.ntp.org": "0.001"}
        provider.get_statistics.return_value = {
            "last_sync": "2025-01-11T12:00:00.000Z",
            "sync_count": 1,
        }
        yield provider


@pytest.fixture
def mock_blockchain_verifier():
    """Mock blockchain verifier that returns predictable values."""
    with patch("src.blockchain_verifier.BlockchainVerifier") as mock:
        verifier = mock.return_value
        verifier.get_blockchain_hashes.return_value = {
            "bitcoin": "00000000000000000008a1234567890abcdef1234567890abcdef1234567890ab"
        }
        verifier.get_statistics.return_value = {
            "last_update": "2025-01-11T12:00:00.000Z",
            "successful_requests": 1,
        }
        yield verifier


@pytest.fixture
def mock_identity_manager():
    """Mock identity manager that returns predictable values."""
    with patch("src.identity_manager.IdentityManager") as mock:
        manager = mock.return_value
        manager.get_identity_hash.return_value = "abc123def456789"
        manager.get_statistics.return_value = {
            "identity_hash": "abc123def456789",
            "files_included": 1,
        }
        yield manager


@pytest.fixture
def mock_qr_generator():
    """Mock QR generator that returns predictable values."""
    with patch("src.qr_generator.QRGenerator") as mock:
        generator = mock.return_value
        generator.generate_qr_image.return_value = b"fake_qr_image_data"
        yield generator


@pytest.fixture
def sample_qr_data() -> QRData:
    """Provide sample QR data for testing."""
    return QRData(
        timestamp="2025-01-11T12:00:00.000Z",
        identity_hash="abc123def456789",
        blockchain_hashes={
            "bitcoin": "00000000000000000008a1234567890abcdef1234567890abcdef1234567890ab"
        },
        time_server_verification={"pool.ntp.org": "0.001"},
        sequence_number=1,
    )


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_data = {
            "update_interval": 2.0,
            "web_settings": {"port": 8082, "host": "localhost"},
            "blockchain_settings": {"enabled_chains": ["bitcoin"]},
        }
        import json

        json.dump(config_data, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def mock_requests():
    """Mock requests library for API testing."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "hash": "00000000000000000008a1234567890abcdef1234567890abcdef1234567890ab"
        }
        yield mock_get


@pytest.fixture
def mock_ntp():
    """Mock NTP library for time testing."""
    with patch("ntplib.NTPClient") as mock_client:
        client = mock_client.return_value
        client.request.return_value.offset = 0.001
        client.request.return_value.delay = 0.005
        yield client


@pytest.fixture
def qrlp_instance(
    sample_config,
    mock_time_provider,
    mock_blockchain_verifier,
    mock_identity_manager,
    mock_qr_generator,
) -> QRLiveProtocol:
    """Provide a fully mocked QRLP instance for testing."""
    return QRLiveProtocol(sample_config)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "web: mark test as requiring web interface")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark tests with "integration" in name as integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)

        # Mark tests with "web" in name as web tests
        if "web" in item.nodeid.lower():
            item.add_marker(pytest.mark.web)

        # Mark tests that might be slow
        if any(
            slow_keyword in item.nodeid.lower()
            for slow_keyword in ["blockchain", "network", "time"]
        ):
            item.add_marker(pytest.mark.slow)
