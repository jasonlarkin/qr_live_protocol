"""
Configuration module for QRLP.

Defines all configuration structures and default values for the QR Live Protocol.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import os


@dataclass
class QRSettings:
    """QR code generation settings."""

    error_correction_level: str = "M"  # L, M, Q, H
    border_size: int = 4
    box_size: int = 10
    fill_color: str = "black"
    back_color: str = "white"
    image_format: str = "PNG"
    max_data_size: int = 2000  # Maximum bytes per QR code


@dataclass
class TimeSettings:
    """Time provider settings."""

    update_interval: float = 1.0  # Seconds between time updates
    time_servers: List[str] = field(
        default_factory=lambda: [
            "time.nist.gov",
            "pool.ntp.org",
            "time.google.com",
            "time.cloudflare.com",
        ]
    )
    timeout: float = 5.0  # Timeout for time server requests
    local_fallback: bool = True  # Use local time if servers unavailable
    timezone: str = "UTC"


@dataclass
class BlockchainSettings:
    """Blockchain verification settings."""

    enabled_chains: Set[str] = field(
        default_factory=lambda: {"bitcoin", "ethereum", "litecoin"}
    )
    api_endpoints: Dict[str, str] = field(
        default_factory=lambda: {
            "bitcoin": "https://blockstream.info/api",
            "ethereum": "https://api.etherscan.io/api",
            "litecoin": "https://api.blockcypher.com/v1/ltc/main",
        }
    )
    cache_duration: int = 300  # Cache blockchain data for 5 minutes
    timeout: float = 10.0
    retry_attempts: int = 3


@dataclass
class IdentitySettings:
    """Identity management settings."""

    identity_file: Optional[str] = None  # Path to identity file
    auto_generate: bool = True  # Generate identity if none exists
    hash_algorithm: str = "sha256"
    include_system_info: bool = True  # Include system info in identity
    include_file_hash: bool = True  # Include file hash if identity_file set


@dataclass
class WebSettings:
    """Web server settings."""

    host: str = "localhost"
    port: int = 8080
    auto_open_browser: bool = True
    template_dir: str = "templates"
    static_dir: str = "static"
    debug: bool = False
    cors_enabled: bool = True


@dataclass
class VerificationSettings:
    """Verification settings."""

    max_time_drift: float = 30.0  # Maximum seconds for time verification
    require_blockchain: bool = False  # Require blockchain verification
    require_time_server: bool = False  # Require time server verification
    min_verifications: int = 1  # Minimum successful verifications required


@dataclass
class SecuritySettings:
    """Security and encryption settings."""

    encrypt_qr_data: bool = False
    encryption_key: Optional[str] = None
    sign_qr_data: bool = False
    private_key_file: Optional[str] = None
    public_key_file: Optional[str] = None


@dataclass
class LoggingSettings:
    """Logging configuration."""

    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class QRLPConfig:
    """Main QRLP configuration container."""

    # Core settings
    update_interval: float = 5.0  # Seconds between QR updates

    # Component settings
    qr_settings: QRSettings = field(default_factory=QRSettings)
    time_settings: TimeSettings = field(default_factory=TimeSettings)
    blockchain_settings: BlockchainSettings = field(default_factory=BlockchainSettings)
    identity_settings: IdentitySettings = field(default_factory=IdentitySettings)
    web_settings: WebSettings = field(default_factory=WebSettings)
    verification_settings: VerificationSettings = field(
        default_factory=VerificationSettings
    )
    security_settings: SecuritySettings = field(default_factory=SecuritySettings)
    logging_settings: LoggingSettings = field(default_factory=LoggingSettings)

    @classmethod
    def from_env(cls) -> "QRLPConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Update from environment variables
        if os.getenv("QRLP_UPDATE_INTERVAL"):
            config.update_interval = float(os.getenv("QRLP_UPDATE_INTERVAL"))

        if os.getenv("QRLP_WEB_PORT"):
            config.web_settings.port = int(os.getenv("QRLP_WEB_PORT"))

        if os.getenv("QRLP_WEB_HOST"):
            config.web_settings.host = os.getenv("QRLP_WEB_HOST")

        if os.getenv("QRLP_IDENTITY_FILE"):
            config.identity_settings.identity_file = os.getenv("QRLP_IDENTITY_FILE")

        if os.getenv("QRLP_LOG_LEVEL"):
            config.logging_settings.level = os.getenv("QRLP_LOG_LEVEL")

        return config

    @classmethod
    def from_file(cls, config_file: str) -> "QRLPConfig":
        """Load configuration from JSON or YAML file."""
        import json

        with open(config_file, "r") as f:
            if config_file.endswith(".json"):
                data = json.load(f)
            elif config_file.endswith((".yml", ".yaml")):
                try:
                    import yaml

                    data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML required for YAML config files")
            else:
                raise ValueError("Config file must be .json, .yml, or .yaml")

        # Create config with data (simplified version)
        config = cls()
        if "update_interval" in data:
            config.update_interval = data["update_interval"]

        # Web settings
        if "web" in data:
            web_data = data["web"]
            if "port" in web_data:
                config.web_settings.port = web_data["port"]
            if "host" in web_data:
                config.web_settings.host = web_data["host"]

        return config

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        from dataclasses import asdict

        return asdict(self)

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        if self.update_interval <= 0:
            issues.append("update_interval must be positive")

        if self.web_settings.port < 1 or self.web_settings.port > 65535:
            issues.append("web port must be between 1 and 65535")

        if self.qr_settings.error_correction_level not in ["L", "M", "Q", "H"]:
            issues.append("QR error correction level must be L, M, Q, or H")

        if self.verification_settings.max_time_drift < 0:
            issues.append("max_time_drift must be non-negative")

        # Check file paths exist if specified
        if self.identity_settings.identity_file and not os.path.exists(
            self.identity_settings.identity_file
        ):
            issues.append(
                f"Identity file not found: {self.identity_settings.identity_file}"
            )

        return issues
