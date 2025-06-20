"""
QR Code Generation module for QRLP.

Handles QR code creation, optimization, and image generation based on the qrkey protocol.
"""

import qrcode
import qrcode.constants

try:
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import (
        RoundedModuleDrawer,
        SquareModuleDrawer,
    )

    STYLED_QR_AVAILABLE = True
except ImportError:
    # Fallback for older qrcode versions
    STYLED_QR_AVAILABLE = False
    StyledPilImage = None
    RoundedModuleDrawer = None
    SquareModuleDrawer = None

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import json
import time
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass

from .config import QRSettings


@dataclass
class QRMetadata:
    """Metadata for QR code generation."""

    data_size: int
    error_correction: str
    version: int
    creation_time: float
    chunk_index: int = 0
    total_chunks: int = 1


class QRGenerator:
    """
    QR Code generator for QRLP.

    Handles creation of QR codes with embedded metadata, chunking for large data,
    and various styling options for livestreaming display.
    """

    # Error correction level mapping
    ERROR_CORRECTION_LEVELS = {
        "L": qrcode.constants.ERROR_CORRECT_L,  # ~7%
        "M": qrcode.constants.ERROR_CORRECT_M,  # ~15%
        "Q": qrcode.constants.ERROR_CORRECT_Q,  # ~25%
        "H": qrcode.constants.ERROR_CORRECT_H,  # ~30%
    }

    def __init__(self, settings: QRSettings):
        """
        Initialize QR generator with settings.

        Args:
            settings: QRSettings configuration object
        """
        self.settings = settings
        self.cache = {}  # Cache for recently generated QR codes
        self.generation_count = 0

    def generate_qr_image(self, data: str, style: Optional[str] = None) -> bytes:
        """
        Generate QR code image as bytes.

        Args:
            data: String data to encode in QR code
            style: Optional style preset ('live', 'professional', 'minimal')

        Returns:
            QR code image as bytes (PNG format)
        """
        # Check cache first
        cache_key = f"{hash(data)}_{style}_{self.settings.error_correction_level}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Create QR code instance
        qr = self._create_qr_instance()

        # Add data and optimize
        qr.add_data(data)
        qr.make(fit=True)

        # Generate image with styling
        img = self._generate_styled_image(qr, style)

        # Convert to bytes
        img_bytes = self._image_to_bytes(img)

        # Cache result (limit cache size)
        if len(self.cache) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[cache_key] = img_bytes
        self.generation_count += 1

        return img_bytes

    def generate_chunked_qr_codes(
        self, data: str, max_chunk_size: Optional[int] = None
    ) -> List[bytes]:
        """
        Generate multiple QR codes for large data by chunking.

        Args:
            data: Large string data to encode
            max_chunk_size: Maximum bytes per chunk (uses config default if None)

        Returns:
            List of QR code image bytes, first one contains metadata
        """
        chunk_size = max_chunk_size or self.settings.max_data_size

        # Split data into chunks
        chunks = self._split_data(data, chunk_size)
        qr_images = []

        # Create metadata QR code
        metadata = QRMetadata(
            data_size=len(data),
            error_correction=self.settings.error_correction_level,
            version=0,  # Will be set after generation
            creation_time=time.time(),
            total_chunks=len(chunks),
        )

        metadata_json = json.dumps(metadata.__dict__)
        metadata_qr = self.generate_qr_image(metadata_json, style="professional")
        qr_images.append(metadata_qr)

        # Create QR codes for each chunk
        for i, chunk in enumerate(chunks):
            chunk_qr = self.generate_qr_image(chunk, style="live")
            qr_images.append(chunk_qr)

        return qr_images

    def create_live_display_qr(self, qr_data: Dict, include_text: bool = True) -> bytes:
        """
        Create QR code optimized for live display with text overlay.

        Args:
            qr_data: Dictionary containing QR data
            include_text: Whether to include readable text overlay

        Returns:
            QR code image with text overlay as bytes
        """
        # Generate base QR code
        qr_json = json.dumps(qr_data, separators=(",", ":"))
        qr_img_bytes = self.generate_qr_image(qr_json, style="live")

        if not include_text:
            return qr_img_bytes

        # Add text overlay
        return self._add_text_overlay(qr_img_bytes, qr_data)

    def verify_qr_readability(self, qr_image: bytes) -> Dict[str, Union[bool, float]]:
        """
        Verify QR code readability and quality metrics.

        Args:
            qr_image: QR code image as bytes

        Returns:
            Dictionary with readability metrics
        """
        try:
            from pyzbar import pyzbar
            import cv2
            import numpy as np

            # Convert bytes to numpy array
            nparr = np.frombuffer(qr_image, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Decode QR code
            decoded_objects = pyzbar.decode(img)

            if decoded_objects:
                return {
                    "readable": True,
                    "confidence": 1.0,
                    "data_length": len(decoded_objects[0].data),
                    "type": decoded_objects[0].type,
                }
            else:
                return {
                    "readable": False,
                    "confidence": 0.0,
                    "error": "Could not decode QR code",
                }

        except ImportError:
            return {
                "readable": None,
                "error": "pyzbar library not available for verification",
            }
        except Exception as e:
            return {"readable": False, "error": str(e)}

    def get_statistics(self) -> Dict:
        """Get generator statistics."""
        return {
            "total_generated": self.generation_count,
            "cache_size": len(self.cache),
            "settings": self.settings.__dict__,
        }

    def _create_qr_instance(self) -> qrcode.QRCode:
        """Create QR code instance with current settings."""
        error_level = self.ERROR_CORRECTION_LEVELS.get(
            self.settings.error_correction_level, qrcode.constants.ERROR_CORRECT_M
        )

        return qrcode.QRCode(
            version=1,  # Auto-determined
            error_correction=error_level,
            box_size=self.settings.box_size,
            border=self.settings.border_size,
        )

    def _generate_styled_image(
        self, qr: qrcode.QRCode, style: Optional[str]
    ) -> Image.Image:
        """Generate styled QR code image."""
        if style == "live" and STYLED_QR_AVAILABLE:
            # High contrast for video streaming
            return qr.make_image(
                fill_color="black",
                back_color="white",
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
            )
        elif style == "professional" and STYLED_QR_AVAILABLE:
            # Rounded corners for professional look
            return qr.make_image(
                fill_color=self.settings.fill_color,
                back_color=self.settings.back_color,
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
            )
        elif style == "minimal":
            # Minimal styling
            return qr.make_image(fill_color="#333333", back_color="#ffffff")
        elif style == "live":
            # Fallback for live style without advanced styling
            return qr.make_image(fill_color="black", back_color="white")
        elif style == "professional":
            # Fallback for professional style
            return qr.make_image(
                fill_color=self.settings.fill_color, back_color=self.settings.back_color
            )
        else:
            # Default styling
            return qr.make_image(
                fill_color=self.settings.fill_color, back_color=self.settings.back_color
            )

    def _split_data(self, data: str, chunk_size: int) -> List[str]:
        """Split data into chunks for multiple QR codes."""
        # Use base64 encoding for binary safety
        encoded_data = base64.b64encode(data.encode("utf-8")).decode("ascii")

        chunks = []
        for i in range(0, len(encoded_data), chunk_size):
            chunks.append(encoded_data[i : i + chunk_size])

        return chunks

    def _image_to_bytes(self, img: Image.Image) -> bytes:
        """Convert PIL Image to bytes."""
        img_buffer = BytesIO()
        img.save(img_buffer, format=self.settings.image_format)
        img_buffer.seek(0)
        return img_buffer.getvalue()

    def _add_text_overlay(self, qr_img_bytes: bytes, qr_data: Dict) -> bytes:
        """Add text overlay to QR code for live display."""
        try:
            # Load QR image
            qr_img = Image.open(BytesIO(qr_img_bytes))

            # Create larger canvas for text
            canvas_width = qr_img.width + 400  # Extra space for text
            canvas_height = qr_img.height + 100
            canvas = Image.new("RGB", (canvas_width, canvas_height), "white")

            # Paste QR code
            qr_x = 20
            qr_y = 50
            canvas.paste(qr_img, (qr_x, qr_y))

            # Add text information
            draw = ImageDraw.Draw(canvas)

            try:
                # Try to load a nice font
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_medium = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 12)
            except (OSError, IOError):
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Text position
            text_x = qr_img.width + 40
            text_y = 50

            # Title
            draw.text(
                (text_x, text_y), "QR Live Protocol", fill="black", font=font_large
            )
            text_y += 40

            # Timestamp
            if "timestamp" in qr_data:
                timestamp_text = f"Time: {qr_data['timestamp'][:19]}"
                draw.text(
                    (text_x, text_y), timestamp_text, fill="black", font=font_medium
                )
                text_y += 30

            # Sequence number
            if "sequence_number" in qr_data:
                seq_text = f"Sequence: #{qr_data['sequence_number']}"
                draw.text((text_x, text_y), seq_text, fill="black", font=font_medium)
                text_y += 30

            # Identity hash (shortened)
            if "identity_hash" in qr_data:
                identity_short = qr_data["identity_hash"][:16] + "..."
                identity_text = f"Identity: {identity_short}"
                draw.text(
                    (text_x, text_y), identity_text, fill="black", font=font_small
                )
                text_y += 25

            # Blockchain info
            if "blockchain_hashes" in qr_data and qr_data["blockchain_hashes"]:
                draw.text(
                    (text_x, text_y),
                    "Blockchain Verified:",
                    fill="green",
                    font=font_small,
                )
                text_y += 20
                for chain in list(qr_data["blockchain_hashes"].keys())[
                    :3
                ]:  # Show max 3
                    draw.text(
                        (text_x + 10, text_y),
                        f"• {chain.title()}",
                        fill="green",
                        font=font_small,
                    )
                    text_y += 18

            # Convert back to bytes
            return self._image_to_bytes(canvas)

        except Exception as e:
            # Return original QR if text overlay fails
            print(f"Text overlay error: {e}")
            return qr_img_bytes
