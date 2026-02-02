"""
Full content pipeline.

End-to-end content generation: music → image → video → merge.
Supports local-first output with optional upload to destinations.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Any

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.pipelines.base import PipelineResult, PipelineConfig
from ai_content.pipelines.music import MusicPipeline
from ai_content.pipelines.video import VideoPipeline
from ai_content.presets.music import get_preset as get_music_preset
from ai_content.presets.video import get_preset as get_video_preset
from ai_content.utils.file_handlers import generate_output_path

logger = logging.getLogger(__name__)


class FullContentPipeline:
    """
    End-to-end content generation pipeline.

    Orchestrates:
    1. Music generation (parallel with image)
    2. Image generation (for video keyframe)
    3. Video generation (from image)
    4. Media merge (audio + video)
    5. Local export (always)
    6. Optional upload (YouTube, S3)

    Example:
        >>> pipeline = FullContentPipeline()
        >>> result = await pipeline.generate_music_video(
        ...     music_style="jazz",
        ...     video_style="urban",
        ...     upload_to="youtube",  # or "s3", "local"
        ... )
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
        music_provider: str = "lyria",
        video_provider: str = "veo",
        image_provider: str = "imagen",
    ):
        self.config = config or PipelineConfig()
        self.music_provider = music_provider
        self.video_provider = video_provider
        self.image_provider = image_provider

        self.music_pipeline = MusicPipeline(config, music_provider)
        self.video_pipeline = VideoPipeline(config, video_provider)

    async def generate_music_video(
        self,
        music_style: str = "jazz",
        video_style: str = "nature",
        *,
        music_provider: str | None = None,
        video_provider: str | None = None,
        parallel_generation: bool = True,
        generate_keyframe: bool = True,
        keyframe_image: str | Path | None = None,
        merge_audio_video: bool = True,
        upload_to: str | None = None,  # "youtube", "s3", or None for local only
    ) -> PipelineResult:
        """
        Generate a complete music video.

        Pipeline steps:
        1. Generate music and keyframe image (parallel)
        2. Generate video from keyframe
        3. Merge audio and video
        4. Export locally
        5. Optionally upload

        Args:
            music_style: Music preset name
            video_style: Video preset name
            music_provider: Override music provider
            video_provider: Override video provider
            parallel_generation: Run music/image in parallel
            generate_keyframe: Generate keyframe with Imagen
            keyframe_image: Use existing image instead of generating
            merge_audio_video: Merge audio and video with FFmpeg
            upload_to: Upload destination ("youtube", "s3", or None)

        Returns:
            PipelineResult with all outputs
        """
        result = PipelineResult(success=True)
        result.metadata["workflow"] = "full-music-video"
        result.metadata["music_style"] = music_style
        result.metadata["video_style"] = video_style

        logger.info("=" * 60)
        logger.info("🎬 Full Content Pipeline: Music Video")
        logger.info("=" * 60)
        logger.info(f"   Music: {music_style} ({music_provider or self.music_provider})")
        logger.info(f"   Video: {video_style} ({video_provider or self.video_provider})")

        # Get presets
        music_preset = get_music_preset(music_style)
        video_preset = get_video_preset(video_style)

        # Phase 1: Generate music and keyframe (parallel)
        logger.info("\n📍 Phase 1: Content Generation")

        tasks = []

        # Music generation task
        async def generate_music():
            logger.info("   🎵 Generating music...")
            provider = ProviderRegistry.get_music(music_provider or self.music_provider)
            return await provider.generate(
                prompt=music_preset.prompt if music_preset else f"[{music_style}] Instrumental",
                bpm=music_preset.bpm if music_preset else 120,
                duration_seconds=30,
            )

        tasks.append(generate_music())

        # Image generation task (if needed)
        image_result: GenerationResult | None = None

        if generate_keyframe and not keyframe_image:

            async def generate_image():
                logger.info("   🖼️  Generating keyframe image...")
                try:
                    provider = ProviderRegistry.get_image(self.image_provider)
                    # Create prompt from video style
                    image_prompt = video_preset.prompt if video_preset else "Cinematic scene"
                    image_prompt = f"Still frame, {image_prompt.split(',')[0]}, photorealistic"
                    return await provider.generate(
                        prompt=image_prompt,
                        aspect_ratio=video_preset.aspect_ratio if video_preset else "16:9",
                    )
                except Exception as e:
                    logger.warning(f"   ⚠️ Image generation skipped: {e}")
                    return GenerationResult(
                        success=False,
                        provider=self.image_provider,
                        content_type="image",
                        error=str(e),
                    )

            tasks.append(generate_image())

        if parallel_generation and len(tasks) > 1:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            music_result = results[0] if not isinstance(results[0], Exception) else None
            image_result = (
                results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None
            )
        else:
            music_result = await tasks[0]
            if len(tasks) > 1:
                image_result = await tasks[1]

        # Handle music result
        if music_result and isinstance(music_result, GenerationResult):
            result.add_output("music", music_result)
            if music_result.success:
                logger.info(f"   ✅ Music: {music_result.file_path}")
            else:
                logger.error(f"   ❌ Music failed: {music_result.error}")

        # Handle image result
        if image_result and isinstance(image_result, GenerationResult):
            result.add_output("keyframe", image_result)
            if image_result.success:
                logger.info(f"   ✅ Keyframe: {image_result.file_path}")

        # Determine keyframe source
        keyframe_source = keyframe_image
        if not keyframe_source and image_result and image_result.success:
            keyframe_source = image_result.file_path

        # Phase 2: Generate video
        logger.info("\n📍 Phase 2: Video Generation")

        if keyframe_source:
            logger.info(f"   🎬 Generating video from keyframe...")
            try:
                provider = ProviderRegistry.get_video(video_provider or self.video_provider)
                video_result = await provider.generate(
                    prompt=video_preset.prompt if video_preset else "Cinematic motion",
                    first_frame=str(keyframe_source),
                    aspect_ratio=video_preset.aspect_ratio if video_preset else "16:9",
                    duration_seconds=5,
                )
                result.add_output("video", video_result)

                if video_result.success:
                    logger.info(f"   ✅ Video: {video_result.file_path}")
            except Exception as e:
                logger.error(f"   ❌ Video generation failed: {e}")
                result.errors.append(f"Video: {e}")
        else:
            # Text-to-video fallback
            logger.info("   🎬 Generating video from text (no keyframe)...")
            try:
                provider = ProviderRegistry.get_video(video_provider or self.video_provider)
                video_result = await provider.generate(
                    prompt=video_preset.prompt if video_preset else "Cinematic scene",
                    aspect_ratio=video_preset.aspect_ratio if video_preset else "16:9",
                    duration_seconds=5,
                )
                result.add_output("video", video_result)

                if video_result.success:
                    logger.info(f"   ✅ Video: {video_result.file_path}")
            except Exception as e:
                logger.error(f"   ❌ Video generation failed: {e}")
                result.errors.append(f"Video: {e}")

        # Phase 3: Merge audio and video
        if merge_audio_video:
            await self._merge_audio_video(result)

        # Phase 4: Upload (if requested)
        if upload_to:
            await self._upload_output(result, upload_to)

        # Finalize
        result.success = bool(
            result.outputs.get("music", {}).success or result.outputs.get("video", {}).success
        )

        logger.info("\n" + "=" * 60)
        logger.info(f"🏁 Pipeline Complete: {'✅ Success' if result.success else '❌ Failed'}")
        logger.info(f"   Duration: {result.duration_seconds:.1f}s")
        logger.info(f"   Outputs: {len(result.output_files)} files")
        logger.info("=" * 60)

        return result.complete()

    async def _merge_audio_video(self, result: PipelineResult) -> None:
        """Merge audio and video using FFmpeg."""
        logger.info("\n📍 Phase 3: Media Merge")

        music = result.outputs.get("music")
        video = result.outputs.get("video")

        if not (music and music.success and video and video.success):
            logger.warning("   ⚠️ Skipping merge: missing music or video")
            return

        try:
            # Import here to make FFmpeg optional
            from ai_content.integrations.media import MediaProcessor

            processor = MediaProcessor()
            merged_path = generate_output_path(
                self.config.output_dir,
                "music_video",
                "mp4",
            )

            logger.info("   🔀 Merging audio and video...")
            await processor.merge_audio_video(
                audio_path=music.file_path,
                video_path=video.file_path,
                output_path=merged_path,
            )

            result.add_output(
                "merged",
                GenerationResult(
                    success=True,
                    provider="ffmpeg",
                    content_type="video",
                    file_path=merged_path,
                ),
            )
            logger.info(f"   ✅ Merged: {merged_path}")

        except ImportError:
            logger.warning("   ⚠️ FFmpeg not available, skipping merge")
        except Exception as e:
            logger.error(f"   ❌ Merge failed: {e}")
            result.errors.append(f"Merge: {e}")

    async def _upload_output(self, result: PipelineResult, destination: str) -> None:
        """Upload output to destination."""
        logger.info(f"\n📍 Phase 4: Upload to {destination}")

        # Get best output file
        output_file = None
        for key in ["merged", "video", "music"]:
            output = result.outputs.get(key)
            if output and output.success and output.file_path:
                output_file = output.file_path
                break

        if not output_file:
            logger.warning("   ⚠️ No output file to upload")
            return

        if destination == "youtube":
            try:
                from ai_content.integrations.youtube import YouTubeUploader

                uploader = YouTubeUploader()

                title = f"AI Generated: {result.metadata.get('music_style', 'Music')} Video"
                video_id = await uploader.upload(
                    video_path=output_file,
                    title=title,
                    description="Generated with ai-content package",
                )

                result.metadata["youtube_id"] = video_id
                logger.info(f"   ✅ Uploaded to YouTube: {video_id}")

            except ImportError:
                logger.warning("   ⚠️ YouTube integration not available")
            except Exception as e:
                logger.error(f"   ❌ YouTube upload failed: {e}")
                result.errors.append(f"YouTube: {e}")

        elif destination == "s3":
            logger.info("   📦 S3 upload not yet implemented")
            result.metadata["note"] = "S3 upload pending implementation"

        else:
            logger.info(f"   ✅ Local export complete: {output_file}")
