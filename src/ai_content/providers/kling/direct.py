"""
KlingAI direct video provider.

Uses JWT authentication for the KlingAI API.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import jwt

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.core.exceptions import (
    ProviderError,
    AuthenticationError,
)
from ai_content.config import get_settings

logger = logging.getLogger(__name__)


@ProviderRegistry.register_video("kling")
class KlingDirectProvider:
    """
    KlingAI direct API video provider.

    Features:
        - Highest quality video generation
        - v2.1-master model
        - JWT authentication
        - Note: Takes 5-14 minutes to generate

    Example:
        >>> provider = KlingDirectProvider()
        >>> result = await provider.generate(
        ...     "Dragon soaring over mountains",
        ...     aspect_ratio="16:9",
        ... )
    """

    name = "kling"
    supports_image_to_video = True
    max_duration_seconds = 10

    def __init__(self):
        self.settings = get_settings().kling

    def _generate_token(self) -> str:
        """Generate JWT token for authentication."""
        if not self.settings.api_key or not self.settings.secret_key:
            raise AuthenticationError("kling")

        payload = {
            "iss": self.settings.api_key,
            "exp": int(time.time()) + 1800,  # 30 minutes
            "nbf": int(time.time()) - 5,
        }

        return jwt.encode(payload, self.settings.secret_key, algorithm="HS256")

    @property
    def headers(self) -> dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self._generate_token()}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        duration_seconds: int = 5,
        first_frame_url: str | None = None,
        output_path: str | None = None,
        mode: str = "std",
    ) -> GenerationResult:
        """
        Generate video using KlingAI v2.1-master.

        Args:
            prompt: Scene description
            aspect_ratio: "16:9", "9:16", or "1:1"
            duration_seconds: Video length ("5" or "10")
            first_frame_url: Optional image URL for image-to-video
            output_path: Where to save the video
            mode: "std" (standard) or "pro"
        """
        logger.info(f"🎬 KlingAI: Generating video (5-14 min expected)")
        logger.debug(f"   Prompt: {prompt[:50]}...")

        try:
            # Determine endpoint
            if first_frame_url:
                endpoint = f"{self.settings.base_url}/v1/videos/image2video"
            else:
                endpoint = f"{self.settings.base_url}/v1/videos/text2video"

            # Build payload
            payload = {
                "model_name": self.settings.model,
                "prompt": prompt,
                "mode": mode,
                "aspect_ratio": aspect_ratio,
                "duration": str(min(duration_seconds, 10)),
            }

            if first_frame_url:
                payload["image_url"] = first_frame_url

            # Submit generation
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                result = response.json()

            task_id = result.get("data", {}).get("task_id")
            if not task_id:
                return GenerationResult(
                    success=False,
                    provider=self.name,
                    content_type="video",
                    error="No task ID in response",
                )

            logger.info(f"   Task ID: {task_id}")

            # Poll for completion
            video_url = await self._poll_for_completion(task_id)

            if not video_url:
                return GenerationResult(
                    success=False,
                    provider=self.name,
                    content_type="video",
                    error="Generation failed or timed out",
                    generation_id=task_id,
                )

            # Download video
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                video_data = response.content

            # Save
            if output_path:
                file_path = Path(output_path)
            else:
                output_dir = get_settings().output_dir
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                file_path = output_dir / f"kling_{timestamp}.mp4"

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(video_data)

            logger.info(f"✅ KlingAI: Saved to {file_path}")

            return GenerationResult(
                success=True,
                provider=self.name,
                content_type="video",
                file_path=file_path,
                data=video_data,
                generation_id=task_id,
                metadata={
                    "aspect_ratio": aspect_ratio,
                    "model": self.settings.model,
                    "prompt": prompt,
                },
            )

        except Exception as e:
            logger.error(f"KlingAI generation failed: {e}")
            return GenerationResult(
                success=False,
                provider=self.name,
                content_type="video",
                error=str(e),
            )

    async def _poll_for_completion(self, task_id: str) -> str | None:
        """Poll until video is ready."""
        status_url = f"{self.settings.base_url}/v1/videos/text2video/{task_id}"

        for attempt in range(self.settings.max_poll_attempts):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        status_url,
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    status = response.json()

                data = status.get("data", {})
                task_status = data.get("task_status", "")

                if task_status == "succeed":
                    videos = data.get("task_result", {}).get("videos", [])
                    if videos:
                        return videos[0].get("url")
                    return None

                if task_status == "failed":
                    error = data.get("task_status_msg", "Unknown error")
                    raise ProviderError("kling", error)

                logger.debug(
                    f"   Poll {attempt + 1}/{self.settings.max_poll_attempts}: {task_status}"
                )

            except httpx.HTTPError as e:
                logger.warning(f"   Poll error: {e}")

            await asyncio.sleep(self.settings.poll_interval)

        return None
