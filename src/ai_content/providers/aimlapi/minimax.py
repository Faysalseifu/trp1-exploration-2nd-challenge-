"""
MiniMax Music provider via AIMLAPI.

Supports reference audio and lyrics.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.providers.aimlapi.client import AIMLAPIClient
from ai_content.config import get_settings

logger = logging.getLogger(__name__)


@ProviderRegistry.register_music("minimax")
class MiniMaxMusicProvider:
    """
    MiniMax Music 2.0 provider via AIMLAPI.

    Features:
        - Reference audio for style transfer
        - Lyrics with structure tags
        - Non-English vocal support
        - High-quality output

    Example:
        >>> provider = MiniMaxMusicProvider()
        >>> result = await provider.generate(
        ...     "Lo-fi hip-hop ambient",
        ...     lyrics="[Verse] Walking through the rain...",
        ... )
    """

    name = "minimax"
    supports_vocals = True
    supports_realtime = False
    supports_reference_audio = True

    def __init__(self):
        self.settings = get_settings().aimlapi
        self.client = AIMLAPIClient()

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
        Generate music using MiniMax Music 2.0.

        Args:
            prompt: Style description
            bpm: Ignored (MiniMax determines tempo)
            duration_seconds: Approximate duration
            lyrics: Lyrics with structure tags
            reference_audio_url: URL for style transfer
            output_path: Where to save the audio
        """
        logger.info(f"🎵 MiniMax: Generating music")
        logger.debug(f"   Prompt: {prompt[:50]}...")
        if lyrics:
            logger.debug(f"   Lyrics: {len(lyrics)} characters")

        try:
            # Build payload
            payload = {
                "model": self.settings.music_model,
                "prompt": prompt,
            }

            if lyrics:
                payload["lyrics"] = lyrics
            if reference_audio_url:
                payload["reference_audio_url"] = reference_audio_url

            # Submit generation
            result = await self.client.submit_generation(
                "/v2/generate/audio",
                payload,
            )

            generation_id = result.get("id") or result.get("generation_id")
            if not generation_id:
                return GenerationResult(
                    success=False,
                    provider=self.name,
                    content_type="music",
                    error="No generation ID in response",
                )

            # Poll for completion
            status = await self.client.wait_for_completion(
                "/v2/generate/audio",
                generation_id,
                check_complete=self._check_complete,
            )

            # Get audio URL
            audio_url = self._extract_audio_url(status)
            if not audio_url:
                return GenerationResult(
                    success=False,
                    provider=self.name,
                    content_type="music",
                    error="No audio URL in response",
                    generation_id=generation_id,
                )

            # Download audio
            audio_data = await self.client.download_file(audio_url)

            # Save
            if output_path:
                file_path = Path(output_path)
            else:
                output_dir = get_settings().output_dir
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                file_path = output_dir / f"minimax_{timestamp}.mp3"

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(audio_data)

            logger.info(f"✅ MiniMax: Saved to {file_path}")

            return GenerationResult(
                success=True,
                provider=self.name,
                content_type="music",
                file_path=file_path,
                data=audio_data,
                generation_id=generation_id,
                metadata={
                    "prompt": prompt,
                    "has_lyrics": lyrics is not None,
                    "has_reference": reference_audio_url is not None,
                },
            )

        except Exception as e:
            logger.error(f"MiniMax generation failed: {e}")
            return GenerationResult(
                success=False,
                provider=self.name,
                content_type="music",
                error=str(e),
            )

    def _check_complete(self, status: dict) -> bool:
        """Check if generation is complete."""
        state = status.get("status") or status.get("state", "")
        return state.lower() in ("completed", "done", "success")

    def _extract_audio_url(self, status: dict) -> str | None:
        """Extract audio URL from status response.

        AIMLAPI music-2.0 returns: {"audio_file": {"url": "..."}}
        """
        # music-2.0 format (per docs)
        if "audio_file" in status:
            audio_file = status["audio_file"]
            if isinstance(audio_file, dict):
                return audio_file.get("url")
        # Try other common formats
        if "audio_url" in status:
            return status["audio_url"]
        if "url" in status:
            return status["url"]
        if "output" in status:
            output = status["output"]
            if isinstance(output, str):
                return output
            if isinstance(output, dict):
                return output.get("audio_url") or output.get("url")
            if isinstance(output, list) and output:
                return output[0].get("audio_url") or output[0].get("url")
        if "result" in status:
            result = status["result"]
            if isinstance(result, dict):
                return result.get("audio_url") or result.get("url")
        return None
