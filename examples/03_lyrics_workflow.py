#!/usr/bin/env python3
"""
Example 03: Lyrics-First Workflow

Demonstrates the Lyrics-First approach:
1. Write or load lyrics
2. Add structure tags automatically
3. Generate music with vocals using MiniMax

This workflow is best when you have specific lyrics you want sung.

Run:
    python examples/03_lyrics_workflow.py

    # With your own lyrics file
    python examples/03_lyrics_workflow.py path/to/lyrics.txt
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.utils.lyrics_parser import parse_lyrics_with_structure
from ai_content.pipelines.music import MusicPipeline

# Import providers
import ai_content.providers  # noqa: F401


# Sample lyrics for demonstration
SAMPLE_LYRICS = """
Walking through the midnight rain
City lights reflect my pain
Every step brings memories
Of the love we used to feel

This is where I belong
This is where I find my song
Through the darkness and the doubt
Love will always lead me out

Morning sun will rise again
Healing starts where heartbreak ends
I'll keep singing through the night
Till I find my way back to the light

This is where I belong
This is where I find my song
Through the darkness and the doubt
Love will always lead me out
"""


async def lyrics_workflow(lyrics_file: str | None = None):
    """Generate music with lyrics."""

    print("🎵 Lyrics-First Workflow Demo")
    print("=" * 50)

    # Load lyrics
    if lyrics_file and Path(lyrics_file).exists():
        print(f"📄 Loading lyrics from: {lyrics_file}")
        lyrics = Path(lyrics_file).read_text()
    else:
        print("📄 Using sample lyrics")
        lyrics = SAMPLE_LYRICS

    # Parse and add structure
    print("\n🔧 Processing lyrics...")
    structured = parse_lyrics_with_structure(lyrics, style="soul")

    print(f"   Verses: {structured.verse_count}")
    print(f"   Choruses: {structured.chorus_count}")
    print(f"   Style Header: {structured.style_header}")

    print("\n📝 Structured Lyrics Preview:")
    print("-" * 40)
    # Show first few lines
    preview_lines = structured.structured.split("\n")[:15]
    for line in preview_lines:
        print(f"   {line}")
    print("   ...")
    print("-" * 40)

    # Generate music with MusicPipeline
    print("\n🎤 Generating music with vocals...")

    pipeline = MusicPipeline()
    result = await pipeline.lyrics_first(
        lyrics=lyrics,
        style="soul",
        provider="minimax",
    )

    if result.success:
        print(f"\n✅ Success!")
        for key, output in result.outputs.items():
            if output.file_path:
                print(f"   {key}: {output.file_path}")
    else:
        print(f"\n❌ Failed: {result.errors}")


if __name__ == "__main__":
    lyrics_file = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(lyrics_workflow(lyrics_file))
