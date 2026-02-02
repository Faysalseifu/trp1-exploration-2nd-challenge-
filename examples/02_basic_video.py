#!/usr/bin/env python3
"""
Example 02: Basic Video Generation

Generate video with ai-content using Veo provider.

Run:
    python examples/02_basic_video.py

    # With different style
    python examples/02_basic_video.py space
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.core.registry import ProviderRegistry
from ai_content.presets.video import get_preset as get_video_preset
import ai_content.providers  # noqa: F401


async def generate_video(style: str = "nature"):
    """Generate video with a preset style."""

    print(f"🎬 Generating {style} video...")

    # Get the preset
    preset = get_video_preset(style)
    if not preset:
        print(f"❌ Unknown style: {style}")
        print(f"   Available: nature, urban, space, abstract, fantasy, aerial, underwater")
        return

    print(f"   Prompt: {preset.prompt[:60]}...")
    print(f"   Aspect Ratio: {preset.aspect_ratio}")

    # Get the Veo provider
    provider = ProviderRegistry.get_video("veo")

    # Generate
    result = await provider.generate(
        prompt=preset.prompt,
        aspect_ratio=preset.aspect_ratio,
        duration_seconds=5,
    )

    if result.success:
        print(f"✅ Generated: {result.file_path}")
    else:
        print(f"❌ Failed: {result.error}")


if __name__ == "__main__":
    style = sys.argv[1] if len(sys.argv) > 1 else "nature"
    asyncio.run(generate_video(style))
