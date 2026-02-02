"""
Music generation pipelines.

Provides orchestrated workflows for music generation including:
- Performance-First: Instrumental first, then lyrics later
- Lyrics-First: Structure lyrics before generation
- Reference-Based: Style transfer from reference audio
"""

import logging
from pathlib import Path
from typing import Optional

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.pipelines.base import PipelineResult, PipelineConfig
from ai_content.presets.music import get_preset as get_music_preset, MUSIC_PRESETS
from ai_content.utils.lyrics_parser import parse_lyrics_with_structure

logger = logging.getLogger(__name__)


class MusicPipeline:
    """
    Music generation pipeline with multiple workflow strategies.

    Example:
        >>> pipeline = MusicPipeline()
        >>> result = await pipeline.performance_first("jazz")
        >>> print(result.outputs["music"].file_path)
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
        default_provider: str = "lyria",
    ):
        self.config = config or PipelineConfig()
        self.default_provider = default_provider

    async def performance_first(
        self,
        style: str = "jazz",
        *,
        provider: str | None = None,
        duration: int = 30,
        bpm: int | None = None,
    ) -> PipelineResult:
        """
        Performance-First workflow (recommended).

        Generates instrumental music first, letting the AI "hallucinate"
        the perfect performance. User can then write lyrics to match.

        Args:
            style: Music style preset name
            provider: Provider to use (default: lyria)
            duration: Duration in seconds
            bpm: Beats per minute (uses preset default if not specified)

        Returns:
            PipelineResult with generated music
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "performance-first"
        result.metadata["style"] = style

        logger.info(f"🎵 Performance-First Workflow: {style}")
        logger.info("   Strategy: Generate instrumental, let AI find the groove")

        # Get preset
        preset = get_music_preset(style)
        if not preset:
            preset = MUSIC_PRESETS.get("jazz")

        # Build prompt emphasizing instrumental/no lyrics
        prompt = f"""[{style.title()} Style]
[Instrumental, No Vocals]
{preset.prompt if preset else "Smooth jazz fusion"}
Let the music breathe with natural feel"""

        provider_name = provider or self.default_provider

        try:
            music_provider = ProviderRegistry.get_music(provider_name)

            gen_result = await music_provider.generate(
                prompt=prompt,
                bpm=bpm or (preset.bpm if preset else 120),
                duration_seconds=duration,
            )

            result.add_output("music", gen_result)

            if gen_result.success:
                logger.info(f"✅ Music generated: {gen_result.file_path}")
            else:
                logger.error(f"❌ Generation failed: {gen_result.error}")
                result.success = False

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            result.errors.append(str(e))
            result.success = False

        return result.complete()

    async def lyrics_first(
        self,
        lyrics: str,
        style: str = "pop",
        *,
        provider: str = "minimax",
        auto_structure: bool = True,
    ) -> PipelineResult:
        """
        Lyrics-First workflow.

        Parses raw lyrics, adds structure tags, then generates music.
        Best used with providers that support vocals (MiniMax).

        Args:
            lyrics: Raw lyrics text or path to lyrics file
            style: Music style for formatting
            provider: Provider (should support vocals)
            auto_structure: Whether to auto-detect verse/chorus structure

        Returns:
            PipelineResult with generated music
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "lyrics-first"
        result.metadata["style"] = style

        logger.info(f"🎵 Lyrics-First Workflow: {style}")

        # Load lyrics if path
        lyrics_content = lyrics
        if Path(lyrics).exists():
            lyrics_content = Path(lyrics).read_text()
            logger.info(f"   Loaded lyrics from: {lyrics}")

        # Parse and structure lyrics
        structured = parse_lyrics_with_structure(
            lyrics_content,
            style=style,
            auto_detect_structure=auto_structure,
        )

        logger.info(f"   Verses: {structured.verse_count}, Choruses: {structured.chorus_count}")
        result.metadata["lyrics_stats"] = {
            "verses": structured.verse_count,
            "choruses": structured.chorus_count,
            "has_bridge": structured.has_bridge,
        }

        # Get preset for additional context
        preset = get_music_preset(style)

        # Build prompt with structured lyrics
        prompt = f"""{structured.style_header}
[Emotional Vocal Delivery, Dynamic Performance]

{structured.structured}"""

        try:
            # Check if provider supports vocals
            music_provider = ProviderRegistry.get_music(provider)

            if not music_provider.supports_vocals:
                logger.warning(f"⚠️ {provider} may not support vocals well. Consider 'minimax'.")

            gen_result = await music_provider.generate(
                prompt=prompt,
                lyrics=structured.structured,
                bpm=preset.bpm if preset else 100,
            )

            result.add_output("music", gen_result)

            if gen_result.success:
                logger.info(f"✅ Music with vocals generated: {gen_result.file_path}")
            else:
                result.success = False

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            result.errors.append(str(e))
            result.success = False

        return result.complete()

    async def reference_based(
        self,
        reference_url: str,
        transformation_prompt: str,
        *,
        provider: str = "minimax",
    ) -> PipelineResult:
        """
        Reference-Based workflow.

        Uses a reference audio to guide style while generating new content.
        Only works with providers that support reference audio.

        Args:
            reference_url: URL to reference audio file
            transformation_prompt: Description of desired transformation
            provider: Provider (must support reference audio)

        Returns:
            PipelineResult with generated music
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "reference-based"
        result.metadata["reference_url"] = reference_url

        logger.info("🎵 Reference-Based Workflow")
        logger.info(f"   Reference: {reference_url[:50]}...")
        logger.info(f"   Transform: {transformation_prompt[:50]}...")

        try:
            music_provider = ProviderRegistry.get_music(provider)

            gen_result = await music_provider.generate(
                prompt=transformation_prompt,
                reference_audio=reference_url,
            )

            result.add_output("music", gen_result)

            if gen_result.success:
                logger.info(f"✅ Transformed music generated: {gen_result.file_path}")
            else:
                result.success = False

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            result.errors.append(str(e))
            result.success = False

        return result.complete()

    async def compare_providers(
        self,
        style: str = "jazz",
        providers: list[str] | None = None,
        *,
        duration: int = 30,
    ) -> PipelineResult:
        """
        Compare multiple providers with the same prompt.

        Useful for evaluating which provider works best for a style.

        Args:
            style: Music style preset
            providers: List of providers to compare (default: all registered)
            duration: Duration for each generation

        Returns:
            PipelineResult with outputs from each provider
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "provider-comparison"
        result.metadata["style"] = style

        if providers is None:
            providers = list(ProviderRegistry.list_music())

        logger.info(f"🔬 Provider Comparison: {style}")
        logger.info(f"   Providers: {', '.join(providers)}")

        preset = get_music_preset(style)
        prompt = preset.prompt if preset else f"[{style.title()}] Instrumental music"
        bpm = preset.bpm if preset else 120

        for provider_name in providers:
            logger.info(f"\n   Testing: {provider_name}...")

            try:
                provider = ProviderRegistry.get_music(provider_name)
                gen_result = await provider.generate(
                    prompt=prompt,
                    bpm=bpm,
                    duration_seconds=duration,
                )

                result.add_output(f"music_{provider_name}", gen_result)

                if gen_result.success:
                    logger.info(f"   ✅ {provider_name} succeeded")
                else:
                    logger.warning(f"   ❌ {provider_name} failed: {gen_result.error}")

            except Exception as e:
                logger.error(f"   ❌ {provider_name} error: {e}")
                result.add_output(
                    f"music_{provider_name}",
                    GenerationResult(
                        success=False,
                        provider=provider_name,
                        content_type="music",
                        error=str(e),
                    ),
                )

        # Success if at least one provider succeeded
        result.success = any(output.success for output in result.outputs.values())

        return result.complete()
