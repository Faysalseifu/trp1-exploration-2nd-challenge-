"""
Video generation pipelines.

Provides orchestrated workflows for video generation including:
- Text-to-Video: Generate from text prompts
- Image-to-Video: Animate a keyframe image
"""

import logging
from pathlib import Path
from typing import Optional

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.pipelines.base import PipelineResult, PipelineConfig
from ai_content.presets.video import get_preset as get_video_preset, VIDEO_PRESETS

logger = logging.getLogger(__name__)


class VideoPipeline:
    """
    Video generation pipeline with multiple input strategies.

    Example:
        >>> pipeline = VideoPipeline()
        >>> result = await pipeline.text_to_video(
        ...     "A dragon soaring through clouds",
        ...     style="fantasy",
        ... )
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
        default_provider: str = "veo",
    ):
        self.config = config or PipelineConfig()
        self.default_provider = default_provider

    async def text_to_video(
        self,
        prompt: str | None = None,
        *,
        style: str | None = None,
        provider: str | None = None,
        aspect_ratio: str | None = None,
        duration: int = 5,
    ) -> PipelineResult:
        """
        Generate video from text prompt.

        Args:
            prompt: Text prompt (uses preset if not provided)
            style: Video style preset name
            provider: Provider to use
            aspect_ratio: Override aspect ratio
            duration: Duration in seconds

        Returns:
            PipelineResult with generated video
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "text-to-video"

        # Get preset if style specified
        preset = get_video_preset(style) if style else None

        # Build prompt
        final_prompt = prompt
        if not final_prompt and preset:
            final_prompt = preset.prompt
        elif not final_prompt:
            final_prompt = VIDEO_PRESETS.get("nature").prompt

        final_aspect_ratio = aspect_ratio or (preset.aspect_ratio if preset else "16:9")

        result.metadata["style"] = style
        result.metadata["aspect_ratio"] = final_aspect_ratio

        logger.info("🎬 Text-to-Video Pipeline")
        logger.info(f"   Prompt: {final_prompt[:60]}...")
        logger.info(f"   Aspect: {final_aspect_ratio}, Duration: {duration}s")

        provider_name = provider or self.default_provider

        try:
            video_provider = ProviderRegistry.get_video(provider_name)

            gen_result = await video_provider.generate(
                prompt=final_prompt,
                aspect_ratio=final_aspect_ratio,
                duration_seconds=duration,
            )

            result.add_output("video", gen_result)

            if gen_result.success:
                logger.info(f"✅ Video generated: {gen_result.file_path}")
            else:
                logger.error(f"❌ Generation failed: {gen_result.error}")
                result.success = False

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            result.errors.append(str(e))
            result.success = False

        return result.complete()

    async def image_to_video(
        self,
        image_source: str | Path,
        prompt: str,
        *,
        provider: str | None = None,
        duration: int = 5,
    ) -> PipelineResult:
        """
        Generate video from keyframe image.

        The image becomes the first frame, and the AI animates it
        according to the prompt.

        Args:
            image_source: Path to image or URL
            prompt: Motion/animation description
            provider: Provider to use
            duration: Duration in seconds

        Returns:
            PipelineResult with generated video
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "image-to-video"
        result.metadata["image_source"] = str(image_source)

        logger.info("🎬 Image-to-Video Pipeline")
        logger.info(f"   Image: {str(image_source)[:50]}...")
        logger.info(f"   Prompt: {prompt[:60]}...")

        provider_name = provider or self.default_provider

        try:
            video_provider = ProviderRegistry.get_video(provider_name)

            gen_result = await video_provider.generate(
                prompt=prompt,
                first_frame=str(image_source),
                duration_seconds=duration,
            )

            result.add_output("video", gen_result)

            if gen_result.success:
                logger.info(f"✅ Video animated: {gen_result.file_path}")
            else:
                result.success = False

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            result.errors.append(str(e))
            result.success = False

        return result.complete()

    async def compare_providers(
        self,
        prompt: str | None = None,
        *,
        style: str = "nature",
        providers: list[str] | None = None,
    ) -> PipelineResult:
        """
        Compare multiple video providers.

        Args:
            prompt: Custom prompt (uses preset if not provided)
            style: Video style preset
            providers: List of providers to compare

        Returns:
            PipelineResult with outputs from each provider
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "provider-comparison"
        result.metadata["style"] = style

        if providers is None:
            providers = list(ProviderRegistry.list_video())

        logger.info(f"🔬 Video Provider Comparison: {style}")
        logger.info(f"   Providers: {', '.join(providers)}")

        preset = get_video_preset(style)
        final_prompt = prompt or (preset.prompt if preset else "Cinematic nature scene")

        for provider_name in providers:
            logger.info(f"\n   Testing: {provider_name}...")

            try:
                provider = ProviderRegistry.get_video(provider_name)
                gen_result = await provider.generate(
                    prompt=final_prompt,
                    aspect_ratio=preset.aspect_ratio if preset else "16:9",
                )

                result.add_output(f"video_{provider_name}", gen_result)

                if gen_result.success:
                    logger.info(f"   ✅ {provider_name} succeeded")
                else:
                    logger.warning(f"   ❌ {provider_name} failed")

            except Exception as e:
                logger.error(f"   ❌ {provider_name} error: {e}")
                result.add_output(
                    f"video_{provider_name}",
                    GenerationResult(
                        success=False,
                        provider=provider_name,
                        content_type="video",
                        error=str(e),
                    ),
                )

        result.success = any(output.success for output in result.outputs.values())

        return result.complete()
