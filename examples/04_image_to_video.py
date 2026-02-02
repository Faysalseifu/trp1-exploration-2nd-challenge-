#!/usr/bin/env python3
"""
Example 04: Image-to-Video Workflow

Demonstrates animating a static image into video:
1. Generate or load a keyframe image
2. Use video provider to animate it with motion

Run:
    python examples/04_image_to_video.py

    # With your own image
    python examples/04_image_to_video.py path/to/image.png
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.core.registry import ProviderRegistry
from ai_content.pipelines.video import VideoPipeline
import ai_content.providers  # noqa: F401


async def image_to_video(image_path: str | None = None):
    """Animate an image into video."""

    print("🎬 Image-to-Video Workflow")
    print("=" * 50)

    pipeline = VideoPipeline()

    if image_path and Path(image_path).exists():
        print(f"📷 Using image: {image_path}")

        # Motion prompt - describes how to animate
        motion_prompt = """
        Gentle camera push-in with subtle parallax,
        ambient particles floating in the air,
        soft lighting changes as if clouds passing,
        cinematic smooth motion, dreamlike atmosphere
        """

        result = await pipeline.image_to_video(
            image_source=image_path,
            prompt=motion_prompt,
            provider="veo",  # or "kling" for higher quality
        )
    else:
        print("📷 No image provided, generating text-to-video instead")
        print("   Tip: Pass an image path to animate it")

        result = await pipeline.text_to_video(
            style="fantasy",
            provider="veo",
        )

    if result.success:
        print(f"\n✅ Video generated!")
        for key, output in result.outputs.items():
            if output.file_path:
                print(f"   {key}: {output.file_path}")
    else:
        print(f"\n❌ Failed: {result.errors}")


if __name__ == "__main__":
    image = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(image_to_video(image))
