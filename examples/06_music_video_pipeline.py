#!/usr/bin/env python3
"""
Example 06: Full Music Video Pipeline

End-to-end music video generation:
1. Generate music (parallel with keyframe)
2. Generate keyframe image (optional)
3. Generate video from keyframe
4. Merge audio and video (requires FFmpeg)
5. Export locally

Run:
    python examples/06_music_video_pipeline.py

    # Different styles
    python examples/06_music_video_pipeline.py cinematic space
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.pipelines.full import FullContentPipeline
import ai_content.providers  # noqa: F401


async def create_music_video(
    music_style: str = "jazz",
    video_style: str = "urban",
):
    """Generate a complete music video."""

    print("🎬 Full Music Video Pipeline")
    print("=" * 60)
    print(f"   Music Style: {music_style}")
    print(f"   Video Style: {video_style}")
    print("=" * 60)

    pipeline = FullContentPipeline()

    result = await pipeline.generate_music_video(
        music_style=music_style,
        video_style=video_style,
        parallel_generation=True,
        generate_keyframe=True,  # Generate image for video
        merge_audio_video=True,  # Requires FFmpeg
    )

    print("\n📊 Pipeline Results:")
    print("-" * 40)

    for key, output in result.outputs.items():
        status = "✅" if output.success else "❌"
        if output.success and output.file_path:
            size_mb = output.file_path.stat().st_size / (1024 * 1024)
            print(f"   {status} {key}: {output.file_path.name} ({size_mb:.1f} MB)")
        elif output.error:
            print(f"   {status} {key}: {output.error[:60]}")

    print("-" * 40)
    print(f"   Total Duration: {result.duration_seconds:.1f}s")
    print(f"   Output Files: {len(result.output_files)}")

    if result.output_files:
        print(f"\n📁 Outputs:")
        for path in result.output_files:
            print(f"   → {path}")


if __name__ == "__main__":
    music = sys.argv[1] if len(sys.argv) > 1 else "jazz"
    video = sys.argv[2] if len(sys.argv) > 2 else "urban"
    asyncio.run(create_music_video(music, video))
