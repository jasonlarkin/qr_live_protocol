"""
QR Live Protocol (QRLP)

A comprehensive system for generating and displaying live QR codes that encode
time-stamped, cryptographically verifiable information for livestreaming
and official video releases.

Built on the qrkey protocol for QR code generation and recovery.
"""

__version__ = "1.0.0"
__author__ = "QRLP Development Team (@docxology)"
__email__ = "danielarifriedman@gmail.com"

from .blockchain_verifier import BlockchainVerifier
from .config import QRLPConfig
from .core import QRLiveProtocol
from .identity_manager import IdentityManager
from .qr_generator import QRGenerator
from .time_provider import TimeProvider
from .web_server import QRLiveWebServer

__all__ = [
    "QRLiveProtocol",
    "QRLPConfig",
    "QRGenerator",
    "TimeProvider",
    "BlockchainVerifier",
    "IdentityManager",
    "QRLiveWebServer",
]
