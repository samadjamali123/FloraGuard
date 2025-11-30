"""Utility helpers for the Leaf Disease Detection stack.

This module provides optimized utility functions for image processing
and disease detection using cached detector instances.
"""

from __future__ import annotations

import base64
import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Add the Leaf Disease directory to Python path so FastAPI/CLI can import detector
sys.path.insert(0, str(Path(__file__).parent / "Leaf Disease"))

try:
    from main import LeafDiseaseDetector  # type: ignore
except ImportError as exc:  # pragma: no cover - fatal during startup
    logger.critical(f"Could not import LeafDiseaseDetector: {exc}")
    print(json.dumps({"error": f"Could not import LeafDiseaseDetector: {exc}"}))
    sys.exit(1)


def _ensure_bytes(image_bytes: Optional[bytes]) -> bytes:
    """Validate image bytes input."""
    if not image_bytes:
        raise ValueError("No image bytes provided")
    return image_bytes


def _ensure_base64_string(base64_image_string: Optional[str]) -> str:
    """Validate base64 string input."""
    if not base64_image_string:
        raise ValueError("base64_image_string cannot be empty")
    return base64_image_string


@lru_cache(maxsize=1)
def get_detector() -> LeafDiseaseDetector:
    """Return a cached detector instance to avoid repeated Groq client setup.
    
    The detector is cached at the module level for performance,
    reusing the same Groq API client across requests.
    """
    logger.info("Initializing LeafDiseaseDetector (cached)")
    return LeafDiseaseDetector()


def analyze_leaf_base64(base64_image_string: str) -> Dict[str, Any]:
    """Analyze already-encoded image data and return the detector JSON payload."""
    sanitized = _ensure_base64_string(base64_image_string)
    detector = get_detector()
    return detector.analyze_leaf_image_base64(sanitized)


def convert_image_to_base64(image_bytes: bytes) -> str:
    """Convert raw bytes to base64 for transport."""
    payload = _ensure_bytes(image_bytes)
    return base64.b64encode(payload).decode("utf-8")


def analyze_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """High-level helper used by the API layer to analyze uploaded files."""
    base64_image = convert_image_to_base64(image_bytes)
    return analyze_leaf_base64(base64_image)


def test_with_base64_data(base64_image_string: str) -> Dict[str, Any]:
    """CLI helper mirroring previous behaviour for backwards compatibility."""
    result = analyze_leaf_base64(base64_image_string)
    print(json.dumps(result, indent=2))
    return result


def convert_image_to_base64_and_test(image_bytes: bytes) -> Dict[str, Any]:
    """Preserve legacy function name while delegating to the optimized helpers."""
    result = analyze_image_bytes(image_bytes)
    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    """Allow running this module directly for smoke testing."""
    image_path = Path("Media/brown-spot-4 (1).jpg")
    if not image_path.exists():
        print(json.dumps({"error": f"Test image not found at {image_path}"}))
        return
    convert_image_to_base64_and_test(image_path.read_bytes())


if __name__ == "__main__":
    main()
