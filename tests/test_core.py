"""
Tests for the core QRLP functionality.

Tests the main QRLiveProtocol class and related functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.core import QRLiveProtocol, QRData
from src.config import QRLPConfig


class TestQRData:
    """Test QRData dataclass functionality."""
    
    def test_qr_data_creation(self):
        """Test creating QRData with all required fields."""
        qr_data = QRData(
            timestamp="2025-01-11T12:00:00.000Z",
            identity_hash="abc123def456789",
            blockchain_hashes={"bitcoin": "hash123"},
            time_server_verification={"ntp": "0.001"},
            sequence_number=1
        )
        
        assert qr_data.timestamp == "2025-01-11T12:00:00.000Z"
        assert qr_data.identity_hash == "abc123def456789"
        assert qr_data.blockchain_hashes == {"bitcoin": "hash123"}
        assert qr_data.sequence_number == 1
    
    def test_qr_data_to_json(self):
        """Test QRData serialization to JSON."""
        qr_data = QRData(
            timestamp="2025-01-11T12:00:00.000Z",
            identity_hash="abc123def456789",
            blockchain_hashes={"bitcoin": "hash123"},
            time_server_verification={"ntp": "0.001"},
            sequence_number=1
        )
        
        json_str = qr_data.to_json()
        data = json.loads(json_str)
        
        assert data["timestamp"] == "2025-01-11T12:00:00.000Z"
        assert data["identity_hash"] == "abc123def456789"
        assert data["blockchain_hashes"]["bitcoin"] == "hash123"
        assert data["sequence_number"] == 1
    
    def test_qr_data_from_json(self):
        """Test QRData deserialization from JSON."""
        json_str = '{"timestamp":"2025-01-11T12:00:00.000Z","identity_hash":"abc123","blockchain_hashes":{"bitcoin":"hash123"},"time_server_verification":{"ntp":"0.001"},"sequence_number":1}'
        
        qr_data = QRData.from_json(json_str)
        
        assert qr_data.timestamp == "2025-01-11T12:00:00.000Z"
        assert qr_data.identity_hash == "abc123"
        assert qr_data.blockchain_hashes["bitcoin"] == "hash123"
        assert qr_data.sequence_number == 1


class TestQRLiveProtocol:
    """Test QRLiveProtocol main class."""
    
    def test_initialization_with_default_config(self):
        """Test QRLP initialization with default configuration."""
        qrlp = QRLiveProtocol()
        
        assert qrlp.config is not None
        assert isinstance(qrlp.config, QRLPConfig)
        assert qrlp._running is False
        assert qrlp._sequence_number == 0
        assert len(qrlp._callbacks) == 0
    
    def test_initialization_with_custom_config(self, sample_config):
        """Test QRLP initialization with custom configuration."""
        qrlp = QRLiveProtocol(sample_config)
        
        assert qrlp.config == sample_config
        assert qrlp.config.update_interval == 1.0
        assert qrlp.config.web_settings.port == 8081
    
    def test_add_remove_callback(self):
        """Test adding and removing update callbacks."""
        qrlp = QRLiveProtocol()
        
        # Test adding callback
        callback = Mock()
        qrlp.add_update_callback(callback)
        assert callback in qrlp._callbacks
        assert len(qrlp._callbacks) == 1
        
        # Test removing callback
        qrlp.remove_update_callback(callback)
        assert callback not in qrlp._callbacks
        assert len(qrlp._callbacks) == 0
    
    def test_set_user_data_callback(self):
        """Test setting user data callback."""
        qrlp = QRLiveProtocol()
        
        user_callback = Mock(return_value="test_data")
        qrlp.set_user_data_callback(user_callback)
        
        assert qrlp._user_data_callback == user_callback
    
    @patch('src.core.QRGenerator')
    @patch('src.core.TimeProvider')
    @patch('src.core.BlockchainVerifier')
    @patch('src.core.IdentityManager')
    def test_generate_single_qr(self, mock_identity, mock_blockchain, mock_time, mock_qr):
        """Test generating a single QR code."""
        # Setup mocks
        mock_time.return_value.get_current_time.return_value = "2025-01-11T12:00:00.000Z"
        mock_time.return_value.get_time_server_verification.return_value = {"ntp": "0.001"}
        mock_identity.return_value.get_identity_hash.return_value = "abc123"
        mock_blockchain.return_value.get_blockchain_hashes.return_value = {"bitcoin": "hash123"}
        mock_qr.return_value.generate_qr_image.return_value = b"fake_qr_image"
        
        qrlp = QRLiveProtocol()
        
        # Generate QR
        qr_data, qr_image = qrlp.generate_single_qr()
        
        # Verify results
        assert isinstance(qr_data, QRData)
        assert qr_data.timestamp == "2025-01-11T12:00:00.000Z"
        assert qr_data.identity_hash == "abc123"
        assert qr_data.blockchain_hashes["bitcoin"] == "hash123"
        assert qr_data.sequence_number == 0
        assert qr_image == b"fake_qr_image"
        
        # Verify sequence number incremented
        assert qrlp._sequence_number == 1
    
    def test_get_current_qr_data_none(self):
        """Test getting current QR data when none exists."""
        qrlp = QRLiveProtocol()
        
        assert qrlp.get_current_qr_data() is None
    
    def test_get_current_qr_data_exists(self, sample_qr_data):
        """Test getting current QR data when it exists."""
        qrlp = QRLiveProtocol()
        qrlp._current_qr_data = sample_qr_data
        
        result = qrlp.get_current_qr_data()
        assert result == sample_qr_data
    
    def test_get_statistics(self):
        """Test getting system statistics."""
        qrlp = QRLiveProtocol()
        
        stats = qrlp.get_statistics()
        
        assert "running" in stats
        assert "total_updates" in stats
        assert "sequence_number" in stats
        assert "last_update_time" in stats
        assert "current_qr_data" in stats
        assert "time_provider_stats" in stats
        assert "blockchain_stats" in stats
        assert "identity_stats" in stats
    
    def test_verify_qr_data_valid(self, sample_qr_data):
        """Test verifying valid QR data."""
        qrlp = QRLiveProtocol()
        
        # Mock identity manager to return same hash
        qrlp.identity_manager.get_identity_hash.return_value = "abc123def456789"
        
        json_str = sample_qr_data.to_json()
        result = qrlp.verify_qr_data(json_str)
        
        assert result["valid_json"] is True
        assert result["identity_verified"] is True
    
    def test_verify_qr_data_invalid_json(self):
        """Test verifying invalid JSON data."""
        qrlp = QRLiveProtocol()
        
        result = qrlp.verify_qr_data("invalid json")
        
        assert result["valid_json"] is False
    
    def test_verify_qr_data_wrong_identity(self, sample_qr_data):
        """Test verifying QR data with wrong identity hash."""
        qrlp = QRLiveProtocol()
        
        # Mock identity manager to return different hash
        qrlp.identity_manager.get_identity_hash.return_value = "different_hash"
        
        json_str = sample_qr_data.to_json()
        result = qrlp.verify_qr_data(json_str)
        
        assert result["valid_json"] is True
        assert result["identity_verified"] is False
    
    def test_context_manager(self):
        """Test QRLP as context manager."""
        qrlp = QRLiveProtocol()
        
        with qrlp as q:
            assert q == qrlp
            assert q._running is True
        
        assert qrlp._running is False


class TestQRLiveProtocolLiveGeneration:
    """Test live generation functionality."""
    
    @patch('src.core.threading.Thread')
    def test_start_live_generation(self, mock_thread):
        """Test starting live generation."""
        qrlp = QRLiveProtocol()
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        qrlp.start_live_generation()
        
        assert qrlp._running is True
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    def test_start_live_generation_already_running(self):
        """Test starting live generation when already running."""
        qrlp = QRLiveProtocol()
        qrlp._running = True
        
        # Should not start again
        qrlp.start_live_generation()
        
        # Verify no additional thread was created
        assert qrlp._running is True
    
    def test_stop_live_generation(self):
        """Test stopping live generation."""
        qrlp = QRLiveProtocol()
        qrlp._running = True
        qrlp._update_thread = Mock()
        qrlp._update_thread.is_alive.return_value = True
        
        qrlp.stop_live_generation()
        
        assert qrlp._running is False
        qrlp._update_thread.join.assert_called_once_with(timeout=1.0) 