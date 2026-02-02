#!/usr/bin/env python3
"""
Generate Bachata remix of "Shega Lij Behasabe" by Gosaye Tesfaye.

This script generates a bachata-style version using:
- MiniMax Music 2.0 (supports vocals and lyrics)
- Bachata preset (Dominican romantic style)
- Structured Amharic lyrics with MiniMax tags

Run:
    python examples/shega_lij_bachata_remix.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.pipelines.music import MusicPipeline
from ai_content.presets.music import BACHATA

# Import providers to register them
import ai_content.providers  # noqa: F401


# Path to lyrics file
LYRICS_FILE = Path(__file__).parent.parent / "data/zefen/shega_lij_bachata_lyrics.txt"


async def generate_bachata_remix():
    """Generate bachata-style remix with Amharic lyrics."""

    print("🎵 Shega Lij Bachata Remix Generator")
    print("=" * 55)
    print(f"   Original: Gosaye Tesfaye - Shega Lij Behasabe")
    print(f"   Style: Dominican Bachata Romántica")
    print(f"   BPM: {BACHATA.bpm}")
    print(f"   Mood: {BACHATA.mood}")
    print("=" * 55)

    # Load lyrics
    if LYRICS_FILE.exists():
        lyrics = LYRICS_FILE.read_text()
        print(f"\n📄 Loaded lyrics: {len(lyrics)} characters")
    else:
        print(f"\n❌ Lyrics file not found: {LYRICS_FILE}")
        return

    # Create custom bachata prompt blending Ethiopian and Dominican styles
    custom_prompt = """[Dominican Bachata Romántica with Ethiopian Soul]
[Requinto Guitar Melodic Lead, Güira Rhythm]
[Bongo Patterns, Syncopated Bass Line]
[Romantic Guitar Arpeggios, Emotional Delivery]
[Ethiopian Tizita Modal Influence, Krar-inspired Melodic Phrases]
[Modern Bachata Sensual Elements, Romeo Santos inspired]
Passionate and romantic, blending Latin and Ethiopian musical traditions
Amharic vocals with emotional bachata delivery
"""

    print(f"\n🎸 Prompt Preview:")
    print("-" * 40)
    for line in custom_prompt.strip().split("\n")[:5]:
        print(f"   {line}")
    print("-" * 40)

    # Generate using MusicPipeline with lyrics-first workflow
    print("\n🎤 Generating bachata remix with vocals...")
    print("   Provider: MiniMax Music 2.0")
    print("   This may take 2-3 minutes...\n")

    pipeline = MusicPipeline()

    # Use lyrics_first since we have structured lyrics
    result = await pipeline.lyrics_first(
        lyrics=str(LYRICS_FILE),  # Pass file path
        style="bachata",
        provider="minimax",
        auto_structure=False,  # Already structured
    )

    if result.success:
        print("\n" + "=" * 55)
        print("✅ BACHATA REMIX GENERATED SUCCESSFULLY!")
        print("=" * 55)
        for key, output in result.outputs.items():
            if output.file_path:
                print(f"   📁 File: {output.file_path}")
            if output.file_size_mb:
                print(f"   📊 Size: {output.file_size_mb:.2f} MB")
            if output.duration_seconds:
                print(f"   ⏱️  Duration: {output.duration_seconds}s")
        print("\n   🎧 Enjoy your Ethiopian-Dominican fusion!")
    else:
        print(f"\n❌ Generation failed!")
        for error in result.errors:
            print(f"   Error: {error}")

        # Provide troubleshooting tips
        print("\n💡 Troubleshooting:")
        print("   1. Check AIMLAPI_KEY is set in .env")
        print("   2. Ensure you have API credits remaining")
        print("   3. Try running: make music-minimax STYLE=bachata")


if __name__ == "__main__":
    asyncio.run(generate_bachata_remix())
