"""
AI Content Generation Package

A multi-provider AI content generation framework supporting music, video, and image creation.
"""

__version__ = "0.1.0"
__author__ = "10Academy Training"

from ai_content.core.provider import (
    MusicProvider,
    VideoProvider,
    ImageProvider,
)
from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult

__all__ = [
    "MusicProvider",
    "VideoProvider",
    "ImageProvider",
    "ProviderRegistry",
    "GenerationResult",
    "__version__",
]
