"""
Unit tests for QRData class.

These tests focus on individual method functionality with no external dependencies.
"""

import pytest
import json
from datetime import datetime

from src.core import QRData


class TestQRData:
    """Unit tests for QRData dataclass."""

    @pytest.mark.unit
    def test_qr_data_creation(self):
        """Test creating QRData with all required fields."""
        qr_data = QRData(
            timestamp="2025-01-11T12:00:00.000Z",
            identity_hash="abc123def456789",
            blockchain_hashes={"bitcoin": "hash123"},
            time_server_verification={"ntp": "0.001"},
            sequence_number=1,
        )

        assert qr_data.timestamp == "2025-01-11T12:00:00.000Z"
        assert qr_data.identity_hash == "abc123def456789"
        assert qr_data.blockchain_hashes == {"bitcoin": "hash123"}
        assert qr_data.sequence_number == 1

    @pytest.mark.unit
    def test_qr_data_to_json(self):
        """Test QRData serialization to JSON."""
        qr_data = QRData(
            timestamp="2025-01-11T12:00:00.000Z",
            identity_hash="abc123def456789",
            blockchain_hashes={"bitcoin": "hash123"},
            time_server_verification={"ntp": "0.001"},
            sequence_number=1,
        )

        json_str = qr_data.to_json()
        data = json.loads(json_str)

        assert data["timestamp"] == "2025-01-11T12:00:00.000Z"
        assert data["identity_hash"] == "abc123def456789"
        assert data["blockchain_hashes"]["bitcoin"] == "hash123"
        assert data["sequence_number"] == 1

    @pytest.mark.unit
    def test_qr_data_from_json(self):
        """Test QRData deserialization from JSON."""
        json_str = '{"timestamp":"2025-01-11T12:00:00.000Z","identity_hash":"abc123","blockchain_hashes":{"bitcoin":"hash123"},"time_server_verification":{"ntp":"0.001"},"sequence_number":1}'

        qr_data = QRData.from_json(json_str)

        assert qr_data.timestamp == "2025-01-11T12:00:00.000Z"
        assert qr_data.identity_hash == "abc123"
        assert qr_data.blockchain_hashes["bitcoin"] == "hash123"
        assert qr_data.sequence_number == 1

    @pytest.mark.unit
    def test_qr_data_with_user_data(self):
        """Test QRData with optional user data."""
        user_data = {"message": "Hello World", "user_id": 123}
        qr_data = QRData(
            timestamp="2025-01-11T12:00:00.000Z",
            identity_hash="abc123",
            blockchain_hashes={"bitcoin": "hash123"},
            time_server_verification={"ntp": "0.001"},
            user_data=user_data,
            sequence_number=1,
        )

        assert qr_data.user_data == user_data
        json_str = qr_data.to_json()
        data = json.loads(json_str)
        assert data["user_data"]["message"] == "Hello World"

    @pytest.mark.unit
    def test_qr_data_default_sequence_number(self):
        """Test QRData with default sequence number."""
        qr_data = QRData(
            timestamp="2025-01-11T12:00:00.000Z",
            identity_hash="abc123",
            blockchain_hashes={"bitcoin": "hash123"},
            time_server_verification={"ntp": "0.001"},
        )

        assert qr_data.sequence_number == 0
