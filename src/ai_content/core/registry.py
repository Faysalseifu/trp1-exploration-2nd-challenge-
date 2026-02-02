"""
Provider registry for dynamic provider discovery and instantiation.

Uses decorator-based registration for extensibility.
"""

from typing import Type, TypeVar
import logging

from ai_content.core.provider import MusicProvider, VideoProvider, ImageProvider

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ProviderRegistry:
    """
    Singleton registry for all content generation providers.

    Providers register themselves using decorators, enabling
    plugin-style extensibility without modifying core code.

    Example:
        >>> @ProviderRegistry.register_music("lyria")
        ... class GoogleLyriaProvider:
        ...     # Implementation
        ...     pass

        >>> provider = ProviderRegistry.get_music("lyria")
        >>> result = await provider.generate("jazz")
    """

    _music_providers: dict[str, Type[MusicProvider]] = {}
    _video_providers: dict[str, Type[VideoProvider]] = {}
    _image_providers: dict[str, Type[ImageProvider]] = {}

    # Provider instances (lazy-loaded singletons)
    _music_instances: dict[str, MusicProvider] = {}
    _video_instances: dict[str, VideoProvider] = {}
    _image_instances: dict[str, ImageProvider] = {}

    @classmethod
    def register_music(cls, name: str):
        """
        Decorator to register a music provider.

        Args:
            name: Unique identifier for this provider

        Example:
            >>> @ProviderRegistry.register_music("minimax")
            ... class MiniMaxMusicProvider:
            ...     pass
        """

        def decorator(provider_cls: Type[MusicProvider]) -> Type[MusicProvider]:
            cls._music_providers[name] = provider_cls
            logger.debug(f"Registered music provider: {name}")
            return provider_cls

        return decorator

    @classmethod
    def register_video(cls, name: str):
        """Decorator to register a video provider."""

        def decorator(provider_cls: Type[VideoProvider]) -> Type[VideoProvider]:
            cls._video_providers[name] = provider_cls
            logger.debug(f"Registered video provider: {name}")
            return provider_cls

        return decorator

    @classmethod
    def register_image(cls, name: str):
        """Decorator to register an image provider."""

        def decorator(provider_cls: Type[ImageProvider]) -> Type[ImageProvider]:
            cls._image_providers[name] = provider_cls
            logger.debug(f"Registered image provider: {name}")
            return provider_cls

        return decorator

    @classmethod
    def get_music(cls, name: str) -> MusicProvider:
        """
        Get a music provider instance by name.

        Args:
            name: Provider identifier (e.g., "lyria", "minimax")

        Returns:
            Instantiated provider

        Raises:
            KeyError: If provider not registered
        """
        if name not in cls._music_instances:
            if name not in cls._music_providers:
                available = list(cls._music_providers.keys())
                raise KeyError(
                    f"Music provider '{name}' not found. Available: {available}"
                )
            cls._music_instances[name] = cls._music_providers[name]()
        return cls._music_instances[name]

    @classmethod
    def get_video(cls, name: str) -> VideoProvider:
        """Get a video provider instance by name."""
        if name not in cls._video_instances:
            if name not in cls._video_providers:
                available = list(cls._video_providers.keys())
                raise KeyError(
                    f"Video provider '{name}' not found. Available: {available}"
                )
            cls._video_instances[name] = cls._video_providers[name]()
        return cls._video_instances[name]

    @classmethod
    def get_image(cls, name: str) -> ImageProvider:
        """Get an image provider instance by name."""
        if name not in cls._image_instances:
            if name not in cls._image_providers:
                available = list(cls._image_providers.keys())
                raise KeyError(
                    f"Image provider '{name}' not found. Available: {available}"
                )
            cls._image_instances[name] = cls._image_providers[name]()
        return cls._image_instances[name]

    @classmethod
    def list_music_providers(cls) -> list[str]:
        """List all registered music provider names."""
        return list(cls._music_providers.keys())

    @classmethod
    def list_video_providers(cls) -> list[str]:
        """List all registered video provider names."""
        return list(cls._video_providers.keys())

    @classmethod
    def list_image_providers(cls) -> list[str]:
        """List all registered image provider names."""
        return list(cls._image_providers.keys())

    @classmethod
    def clear(cls):
        """Clear all registrations (useful for testing)."""
        cls._music_providers.clear()
        cls._video_providers.clear()
        cls._image_providers.clear()
        cls._music_instances.clear()
        cls._video_instances.clear()
        cls._image_instances.clear()
