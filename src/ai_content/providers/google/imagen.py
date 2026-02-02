"""
Google Imagen image provider.

Supports Imagen 4 and Gemini experimental image generation.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.core.exceptions import (
    ProviderError,
    AuthenticationError,
)
from ai_content.config import get_settings

logger = logging.getLogger(__name__)


@ProviderRegistry.register_image("imagen")
class GoogleImagenProvider:
    """
    Google Imagen 4 image provider.

    Features:
        - High-quality photorealistic images
        - Multiple aspect ratios
        - Multiple images per request

    Example:
        >>> provider = GoogleImagenProvider()
        >>> result = await provider.generate(
        ...     "Sunset over ocean, 8K, photorealistic",
        ...     aspect_ratio="16:9",
        ... )
    """

    name = "imagen"

    def __init__(self):
        self.settings = get_settings().google
        self._client = None

    def _get_client(self):
        """Lazy-load the Google GenAI client."""
        if self._client is None:
            try:
                from google import genai

                api_key = self.settings.api_key
                if not api_key:
                    raise AuthenticationError("imagen")
                self._client = genai.Client(api_key=api_key)
            except ImportError:
                raise ProviderError(
                    "imagen",
                    "google-genai package not installed. Run: pip install google-genai",
                )
        return self._client

    async def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        num_images: int = 1,
        output_path: str | None = None,
        use_gemini: bool = False,
    ) -> GenerationResult:
        """
        Generate image using Imagen 4 or Gemini.

        Args:
            prompt: Image description
            aspect_ratio: Image aspect ratio
            num_images: Number of images to generate
            output_path: Where to save the image
            use_gemini: Use Gemini experimental instead of Imagen
        """
        from google.genai import types

        client = self._get_client()

        model = (
            self.settings.image_gemini_model
            if use_gemini
            else self.settings.image_model
        )

        logger.info(f"🖼️ Imagen: Generating image ({aspect_ratio})")
        logger.debug(f"   Prompt: {prompt[:50]}...")
        logger.debug(f"   Model: {model}")

        try:
            if use_gemini:
                # Gemini experimental image generation
                response = await client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["image", "text"],
                    ),
                )

                # Find image in response
                image_data = None
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        image_data = part.inline_data.data
                        break

                if not image_data:
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="image",
                        error="No image in Gemini response",
                    )
            else:
                # Imagen 4
                response = await client.aio.models.generate_images(
                    model=model,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=num_images,
                        aspect_ratio=aspect_ratio,
                    ),
                )

                if not response.generated_images:
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="image",
                        error="No images generated",
                    )

                image_data = response.generated_images[0].image.image_bytes

            # Save
            if output_path:
                file_path = Path(output_path)
            else:
                output_dir = get_settings().output_dir
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                file_path = output_dir / f"imagen_{timestamp}.png"

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(image_data)

            logger.info(f"✅ Imagen: Saved to {file_path}")

            return GenerationResult(
                success=True,
                provider=self.name,
                content_type="image",
                file_path=file_path,
                data=image_data,
                metadata={
                    "aspect_ratio": aspect_ratio,
                    "model": model,
                    "prompt": prompt,
                },
            )

        except Exception as e:
            logger.error(f"Imagen generation failed: {e}")
            return GenerationResult(
                success=False,
                provider=self.name,
                content_type="image",
                error=str(e),
            )
