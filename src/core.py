"""
Core QRLP (QR Live Protocol) implementation.

This module provides the main QRLiveProtocol class that coordinates all
components to generate live, verifiable QR codes with time and identity information.
"""

import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

from .blockchain_verifier import BlockchainVerifier
from .config import QRLPConfig
from .identity_manager import IdentityManager
from .qr_generator import QRGenerator
from .time_provider import TimeProvider


@dataclass
class QRData:
    """Structure for QR code data payload."""

    timestamp: str
    identity_hash: str
    blockchain_hashes: Dict[str, str]
    time_server_verification: Dict[str, str]
    user_data: Optional[Dict] = None
    sequence_number: int = 0

    def to_json(self) -> str:
        """Convert to JSON string for QR encoding."""
        return json.dumps(asdict(self), separators=(",", ":"))

    @classmethod
    def from_json(cls, json_str: str) -> "QRData":
        """Create QRData from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


class QRLiveProtocol:
    """
    Main QR Live Protocol coordinator.

    Orchestrates time providers, blockchain verifiers, identity management,
    and QR generation to create live, verifiable QR codes for streaming.
    """

    def __init__(self, config: Optional[QRLPConfig] = None):
        """
        Initialize QRLP with configuration.

        Args:
            config: QRLPConfig object with settings, uses defaults if None
        """
        self.config = config or QRLPConfig()

        # Initialize components
        self.qr_generator = QRGenerator(self.config.qr_settings)
        self.time_provider = TimeProvider(self.config.time_settings)
        self.blockchain_verifier = BlockchainVerifier(self.config.blockchain_settings)
        self.identity_manager = IdentityManager(self.config.identity_settings)

        # State management
        self._running = False
        self._current_qr_data: Optional[QRData] = None
        self._sequence_number = 0
        self._update_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[QRData, bytes], None]] = []

        # User data callback for external input
        self._user_data_callback: Optional[Callable[[], Optional[str]]] = None

        # Performance tracking
        self._last_update_time = 0
        self._update_count = 0

    def add_update_callback(self, callback: Callable[[QRData, bytes], None]) -> None:
        """
        Add callback function to be called when QR code updates.

        Args:
            callback: Function that takes (qr_data, qr_image_bytes) parameters
        """
        self._callbacks.append(callback)

    def remove_update_callback(self, callback: Callable[[QRData, bytes], None]) -> None:
        """Remove previously added callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def set_user_data_callback(self, callback: Callable[[], Optional[str]]) -> None:
        """
        Set callback function to get user data for QR generation.

        Args:
            callback: Function that returns user input string or None
        """
        self._user_data_callback = callback

    def start_live_generation(self) -> None:
        """Start continuous QR code generation in background thread."""
        if self._running:
            return

        self._running = True
        self._update_thread = threading.Thread(
            target=self._update_loop, daemon=True, name="QRLP-Update-Thread"
        )
        self._update_thread.start()

    def stop_live_generation(self) -> None:
        """Stop continuous QR code generation."""
        self._running = False
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)

    def generate_single_qr(
        self, user_data: Optional[Dict] = None
    ) -> tuple[QRData, bytes]:
        """
        Generate a single QR code with current time and verification data.

        Args:
            user_data: Optional additional data to include in QR

        Returns:
            Tuple of (QRData object, QR image as bytes)
        """
        # Gather all verification data
        current_time = self.time_provider.get_current_time()
        identity_hash = self.identity_manager.get_identity_hash()
        blockchain_hashes = self.blockchain_verifier.get_blockchain_hashes()
        time_verification = self.time_provider.get_time_server_verification()

        # Create QR data payload
        qr_data = QRData(
            timestamp=current_time.isoformat(),
            identity_hash=identity_hash,
            blockchain_hashes=blockchain_hashes,
            time_server_verification=time_verification,
            user_data=user_data,
            sequence_number=self._sequence_number,
        )

        # Generate QR code image
        qr_json = qr_data.to_json()
        qr_image = self.qr_generator.generate_qr_image(qr_json)

        # Update sequence number
        self._sequence_number += 1
        self._current_qr_data = qr_data

        return qr_data, qr_image

    def get_current_qr_data(self) -> Optional[QRData]:
        """Get the most recently generated QR data."""
        return self._current_qr_data

    def get_statistics(self) -> Dict:
        """Get performance and usage statistics."""
        return {
            "running": self._running,
            "total_updates": self._update_count,
            "sequence_number": self._sequence_number,
            "last_update_time": self._last_update_time,
            "current_qr_data": (
                asdict(self._current_qr_data) if self._current_qr_data else None
            ),
            "time_provider_stats": self.time_provider.get_statistics(),
            "blockchain_stats": self.blockchain_verifier.get_statistics(),
            "identity_stats": self.identity_manager.get_statistics(),
        }

    def verify_qr_data(self, qr_json: str) -> Dict[str, bool]:
        """
        Verify a QR code's data integrity and authenticity.

        Args:
            qr_json: JSON string from QR code

        Returns:
            Dictionary with verification results for each component
        """
        try:
            qr_data = QRData.from_json(qr_json)

            results = {
                "valid_json": True,
                "identity_verified": False,
                "time_verified": False,
                "blockchain_verified": False,
            }

            # Verify identity hash
            expected_identity = self.identity_manager.get_identity_hash()
            results["identity_verified"] = qr_data.identity_hash == expected_identity

            # Verify time is reasonable (within acceptable window)
            qr_time = datetime.fromisoformat(qr_data.timestamp)
            time_diff = abs((datetime.now(timezone.utc) - qr_time).total_seconds())
            results["time_verified"] = (
                time_diff <= self.config.verification_settings.max_time_drift
            )

            # Verify blockchain hashes (if available)
            if qr_data.blockchain_hashes:
                current_hashes = self.blockchain_verifier.get_blockchain_hashes()
                results["blockchain_verified"] = any(
                    current_hashes.get(chain) == hash_val
                    for chain, hash_val in qr_data.blockchain_hashes.items()
                )

            return results

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return {
                "valid_json": False,
                "error": str(e),
                "identity_verified": False,
                "time_verified": False,
                "blockchain_verified": False,
            }

    def _update_loop(self) -> None:
        """Main update loop for continuous QR generation."""
        while self._running:
            try:
                start_time = time.time()

                # Get user data from callback if available
                user_data = None
                if self._user_data_callback:
                    try:
                        user_text = self._user_data_callback()
                        if user_text:
                            user_data = {"user_text": user_text}
                    except Exception as e:
                        print(f"User data callback error: {e}")

                # Generate new QR code with user data
                qr_data, qr_image = self.generate_single_qr(user_data)

                # Notify all callbacks
                for callback in self._callbacks:
                    try:
                        callback(qr_data, qr_image)
                    except Exception as e:
                        # Log error but continue with other callbacks
                        print(f"Callback error: {e}")

                # Update statistics
                self._last_update_time = start_time
                self._update_count += 1

                # Sleep for remaining interval time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.update_interval - elapsed)
                time.sleep(sleep_time)

            except Exception as e:
                print(f"Update loop error: {e}")
                time.sleep(1.0)  # Prevent tight error loop

    def __enter__(self):
        """Context manager entry."""
        self.start_live_generation()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_live_generation()
