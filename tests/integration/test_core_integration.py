"""
Integration tests for QRLiveProtocol component interactions.

These tests verify that components work together correctly with mocked external dependencies.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.config import QRLPConfig
from src.core import QRLiveProtocol


class TestQRLiveProtocolIntegration:
    """Integration tests for QRLiveProtocol with mocked components."""

    @pytest.mark.integration
    @patch("src.core.QRGenerator")
    @patch("src.core.TimeProvider")
    @patch("src.core.BlockchainVerifier")
    @patch("src.core.IdentityManager")
    def test_component_initialization_integration(
        self, mock_identity, mock_blockchain, mock_time, mock_qr
    ):
        """Test that all components are properly initialized and configured."""
        config = QRLPConfig()
        config.update_interval = 2.0

        qrlp = QRLiveProtocol(config)

        # Verify all components were created with correct config
        mock_qr.assert_called_once_with(config.qr_settings)
        mock_time.assert_called_once_with(config.time_settings)
        mock_blockchain.assert_called_once_with(config.blockchain_settings)
        mock_identity.assert_called_once_with(config.identity_settings)

        # Verify component references
        assert qrlp.qr_generator == mock_qr.return_value
        assert qrlp.time_provider == mock_time.return_value
        assert qrlp.blockchain_verifier == mock_blockchain.return_value
        assert qrlp.identity_manager == mock_identity.return_value

    @pytest.mark.integration
    @patch("src.core.QRGenerator")
    @patch("src.core.TimeProvider")
    @patch("src.core.BlockchainVerifier")
    @patch("src.core.IdentityManager")
    def test_qr_generation_integration(
        self, mock_identity, mock_blockchain, mock_time, mock_qr
    ):
        """Test complete QR generation workflow with mocked components."""
        # Setup mocks
        mock_datetime = datetime(2025, 1, 11, 12, 0, 0)
        mock_time.return_value.get_current_time.return_value = mock_datetime
        mock_time.return_value.get_time_server_verification.return_value = {
            "ntp": "0.001"
        }
        mock_identity.return_value.get_identity_hash.return_value = "abc123"
        mock_blockchain.return_value.get_blockchain_hashes.return_value = {
            "bitcoin": "hash123"
        }
        mock_qr.return_value.generate_qr_image.return_value = b"fake_qr_image"

        qrlp = QRLiveProtocol()

        # Generate QR code
        qr_data, qr_image = qrlp.generate_single_qr()

        # Verify all components were called correctly
        mock_time.return_value.get_current_time.assert_called_once()
        mock_time.return_value.get_time_server_verification.assert_called_once()
        mock_identity.return_value.get_identity_hash.assert_called_once()
        mock_blockchain.return_value.get_blockchain_hashes.assert_called_once()

        # Verify QR generator was called with correct JSON
        mock_qr.return_value.generate_qr_image.assert_called_once()
        call_args = mock_qr.return_value.generate_qr_image.call_args[0][0]
        assert "timestamp" in call_args
        assert "identity_hash" in call_args
        assert "blockchain_hashes" in call_args

        # Verify returned data
        assert qr_data.timestamp == mock_datetime.isoformat()
        assert qr_data.identity_hash == "abc123"
        assert qr_image == b"fake_qr_image"

    @pytest.mark.integration
    @patch("src.core.QRGenerator")
    @patch("src.core.TimeProvider")
    @patch("src.core.BlockchainVerifier")
    @patch("src.core.IdentityManager")
    def test_callback_system_integration(
        self, mock_identity, mock_blockchain, mock_time, mock_qr
    ):
        """Test callback system integration with component updates."""
        # Setup mocks
        mock_datetime = datetime(2025, 1, 11, 12, 0, 0)
        mock_time.return_value.get_current_time.return_value = mock_datetime
        mock_time.return_value.get_time_server_verification.return_value = {
            "ntp": "0.001"
        }
        mock_identity.return_value.get_identity_hash.return_value = "abc123"
        mock_blockchain.return_value.get_blockchain_hashes.return_value = {
            "bitcoin": "hash123"
        }
        mock_qr.return_value.generate_qr_image.return_value = b"fake_qr_image"

        qrlp = QRLiveProtocol()

        # Add callback
        callback = Mock()
        qrlp.add_update_callback(callback)

        # Generate QR code
        qr_data, qr_image = qrlp.generate_single_qr()

        # Verify callback was called with correct data
        callback.assert_called_once_with(qr_data, qr_image)

    @pytest.mark.integration
    @patch("src.core.QRGenerator")
    @patch("src.core.TimeProvider")
    @patch("src.core.BlockchainVerifier")
    @patch("src.core.IdentityManager")
    def test_statistics_integration(
        self, mock_identity, mock_blockchain, mock_time, mock_qr
    ):
        """Test statistics gathering from all components."""
        # Setup mock statistics
        mock_time.return_value.get_statistics.return_value = {"sync_count": 5}
        mock_blockchain.return_value.get_statistics.return_value = {"requests": 10}
        mock_identity.return_value.get_statistics.return_value = {"hash": "abc123"}

        qrlp = QRLiveProtocol()

        # Get statistics
        stats = qrlp.get_statistics()

        # Verify all components were queried for statistics
        mock_time.return_value.get_statistics.assert_called_once()
        mock_blockchain.return_value.get_statistics.assert_called_once()
        mock_identity.return_value.get_statistics.assert_called_once()

        # Verify statistics structure
        assert "time_provider_stats" in stats
        assert "blockchain_stats" in stats
        assert "identity_stats" in stats
        assert stats["time_provider_stats"]["sync_count"] == 5
        assert stats["blockchain_stats"]["requests"] == 10
        assert stats["identity_stats"]["hash"] == "abc123"

    @pytest.mark.integration
    @patch("src.core.QRGenerator")
    @patch("src.core.TimeProvider")
    @patch("src.core.BlockchainVerifier")
    @patch("src.core.IdentityManager")
    def test_verification_integration(
        self, mock_identity, mock_blockchain, mock_time, mock_qr
    ):
        """Test QR verification with component integration."""
        # Setup mocks
        mock_identity.return_value.get_identity_hash.return_value = "abc123"

        qrlp = QRLiveProtocol()

        # Create test QR data
        test_json = '{"timestamp":"2025-01-11T12:00:00.000Z","identity_hash":"abc123","blockchain_hashes":{"bitcoin":"hash123"},"time_server_verification":{"ntp":"0.001"},"sequence_number":1}'

        # Verify QR data
        result = qrlp.verify_qr_data(test_json)

        # Verify identity manager was called for verification
        mock_identity.return_value.get_identity_hash.assert_called_once()

        # Verify verification result
        assert result["valid_json"] is True
        assert result["identity_verified"] is True
