#!/usr/bin/env python3
"""
Example 01: Basic Music Generation

The simplest way to generate music with ai-content.
Uses the Lyria provider with a preset style.

Run:
    python examples/01_basic_music.py

    # With different style
    python examples/01_basic_music.py blues
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.core.registry import ProviderRegistry
from ai_content.presets.music import get_preset as get_music_preset

# Import providers to register them
import ai_content.providers  # noqa: F401


async def generate_music(style: str = "jazz"):
    """Generate music with a preset style."""

    print(f"🎵 Generating {style} music...")

    # Get the preset
    preset = get_music_preset(style)
    if not preset:
        print(f"❌ Unknown style: {style}")
        print(
            f"   Available: jazz, blues, ethiopian-jazz, cinematic, electronic, ambient, lofi, rnb"
        )
        return

    print(f"   Preset: {preset.name}")
    print(f"   BPM: {preset.bpm}")
    print(f"   Mood: {preset.mood}")

    # Get the Lyria provider
    provider = ProviderRegistry.get_music("lyria")

    # Generate
    result = await provider.generate(
        prompt=preset.prompt,
        bpm=preset.bpm,
        duration_seconds=30,
    )

    if result.success:
        print(f"✅ Generated: {result.file_path}")
    else:
        print(f"❌ Failed: {result.error}")


if __name__ == "__main__":
    style = sys.argv[1] if len(sys.argv) > 1 else "jazz"
    asyncio.run(generate_music(style))
