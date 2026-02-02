"""
Core provider protocols and abstractions.

This module defines the interfaces that all providers must implement.
Uses Protocol for structural subtyping (duck typing with type safety).
"""

from typing import Protocol, runtime_checkable
from abc import abstractmethod

from ai_content.core.result import GenerationResult


@runtime_checkable
class MusicProvider(Protocol):
    """
    Protocol for music generation providers.

    Implementations:
        - GoogleLyriaProvider: Real-time streaming, instrumental only
        - MiniMaxMusicProvider: Reference-based, supports lyrics
        - (Future) SunoProvider: Full songs with vocals
        - (Future) UdioProvider: Alternative to Suno

    Example:
        >>> provider = ProviderRegistry.get_music("lyria")
        >>> result = await provider.generate("smooth jazz fusion", bpm=95)
        >>> result.save("output.wav")
    """

    @property
    def name(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    def supports_vocals(self) -> bool:
        """Whether this provider can generate vocals."""
        ...

    @property
    def supports_realtime(self) -> bool:
        """Whether this provider supports real-time streaming."""
        ...

    @property
    def supports_reference_audio(self) -> bool:
        """Whether this provider supports style transfer from reference audio."""
        ...

    async def generate(
        self,
        prompt: str,
        *,
        bpm: int = 120,
        duration_seconds: int = 30,
        lyrics: str | None = None,
        reference_audio_url: str | None = None,
        output_path: str | None = None,
    ) -> GenerationResult:
        """
        Generate music from a text prompt.

        Args:
            prompt: Text description of the music style
            bpm: Beats per minute (tempo)
            duration_seconds: Length of generated audio
            lyrics: Optional lyrics with structure tags [Verse], [Chorus], etc.
            reference_audio_url: Optional URL for style transfer
            output_path: Optional path to save output

        Returns:
            GenerationResult containing audio data or file path
        """
        ...


@runtime_checkable
class VideoProvider(Protocol):
    """
    Protocol for video generation providers.

    Implementations:
        - GoogleVeoProvider: Fast generation, Google native
        - KlingDirectProvider: Highest quality, 5-14 min wait
        - WanProvider: Stable output via AIMLAPI

    Example:
        >>> provider = ProviderRegistry.get_video("kling")
        >>> result = await provider.generate(
        ...     "Dragon soaring over mountains",
        ...     aspect_ratio="16:9"
        ... )
    """

    @property
    def name(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    def supports_image_to_video(self) -> bool:
        """Whether this provider can animate still images."""
        ...

    @property
    def max_duration_seconds(self) -> int:
        """Maximum video duration this provider supports."""
        ...

    async def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        duration_seconds: int = 5,
        first_frame_url: str | None = None,
        output_path: str | None = None,
    ) -> GenerationResult:
        """
        Generate video from a text prompt.

        Args:
            prompt: Text description of the video scene
            aspect_ratio: Video aspect ratio ("16:9", "9:16", "1:1")
            duration_seconds: Video length in seconds
            first_frame_url: Optional image URL to animate
            output_path: Optional path to save output

        Returns:
            GenerationResult containing video data or file path
        """
        ...


@runtime_checkable
class ImageProvider(Protocol):
    """
    Protocol for image generation providers.

    Implementations:
        - GoogleImagenProvider: High-quality photorealistic
        - GeminiImageProvider: Fast, experimental
        - (Future) FluxProvider: Open source quality

    Example:
        >>> provider = ProviderRegistry.get_image("imagen")
        >>> result = await provider.generate("sunset over ocean, 8K")
    """

    @property
    def name(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        num_images: int = 1,
        output_path: str | None = None,
    ) -> GenerationResult:
        """
        Generate image from a text prompt.

        Args:
            prompt: Text description of the image
            aspect_ratio: Image aspect ratio
            num_images: Number of images to generate
            output_path: Optional path to save output

        Returns:
            GenerationResult containing image data or file path
        """
        ...
