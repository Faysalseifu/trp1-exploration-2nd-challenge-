#!/usr/bin/env python3
"""
Example 05: Provider Comparison

Compare multiple providers with the same prompt to evaluate quality.

Run:
    python examples/05_provider_comparison.py

    # Compare video providers
    python examples/05_provider_comparison.py video
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.pipelines.music import MusicPipeline
from ai_content.pipelines.video import VideoPipeline
import ai_content.providers  # noqa: F401


async def compare_music_providers():
    """Compare music generation across providers."""

    print("🔬 Music Provider Comparison")
    print("=" * 60)
    print("   Style: jazz")
    print("   Providers: lyria, minimax")
    print("=" * 60)

    pipeline = MusicPipeline()
    result = await pipeline.compare_providers(
        style="jazz",
        providers=["lyria", "minimax"],
        duration=20,  # Shorter for faster comparison
    )

    print("\n📊 Results:")
    print("-" * 40)

    for key, output in result.outputs.items():
        provider = key.replace("music_", "")
        status = "✅" if output.success else "❌"
        path = output.file_path if output.success else output.error[:50]
        print(f"   {status} {provider}: {path}")

    print("-" * 40)
    print(f"\n   Duration: {result.duration_seconds:.1f}s")


async def compare_video_providers():
    """Compare video generation across providers."""

    print("🔬 Video Provider Comparison")
    print("=" * 60)
    print("   Style: space")
    print("   Providers: veo, kling")
    print("   Note: Kling takes 5-14 minutes")
    print("=" * 60)

    pipeline = VideoPipeline()
    result = await pipeline.compare_providers(
        style="space",
        providers=["veo"],  # Remove kling for faster demo
    )

    print("\n📊 Results:")
    print("-" * 40)

    for key, output in result.outputs.items():
        provider = key.replace("video_", "")
        status = "✅" if output.success else "❌"
        path = (
            output.file_path if output.success else output.error[:50] if output.error else "Unknown"
        )
        print(f"   {status} {provider}: {path}")

    print("-" * 40)
    print(f"\n   Duration: {result.duration_seconds:.1f}s")


async def main(mode: str = "music"):
    if mode == "video":
        await compare_video_providers()
    else:
        await compare_music_providers()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "music"
    asyncio.run(main(mode))
