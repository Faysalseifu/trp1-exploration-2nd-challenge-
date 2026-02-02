"""Google providers module."""

# Import providers to trigger registration
from ai_content.providers.google.lyria import GoogleLyriaProvider
from ai_content.providers.google.veo import GoogleVeoProvider
from ai_content.providers.google.imagen import GoogleImagenProvider

__all__ = [
    "GoogleLyriaProvider",
    "GoogleVeoProvider",
    "GoogleImagenProvider",
]
