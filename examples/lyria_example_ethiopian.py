#!/usr/bin/env python3
"""
Ethiopian-Dominican Bachata Fusion Instrumental Generator

This script demonstrates Google Lyria RealTime music generation with:
- Weighted prompts for style fusion
- Caching to avoid regenerating existing files
- Various Ethiopian music style examples

Usage:
    python examples/lyria_example_ethiopian.py                    # Bachata fusion
    python examples/lyria_example_ethiopian.py --style ethio-jazz # Ethio-Jazz
    python examples/lyria_example_ethiopian.py --force            # Regenerate even if cached
    python examples/lyria_example_ethiopian.py --duration 60      # 60 seconds

Note: Lyria generates INSTRUMENTAL music only (no vocals).
      For vocals, use MiniMax via AIMLAPI.
"""

import argparse
import asyncio
import os
import sys
import wave
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# =============================================================================
# STYLE PRESETS - Weighted Prompts for Different Ethiopian Fusions
# =============================================================================
# Lyria uses weighted prompts (0.0-1.0) to blend styles.
# Higher weight = stronger influence on the generated music.
#
# Tips for good results:
# 1. Use 3-5 weighted prompts for best style blending
# 2. Primary style should have weight 1.0
# 3. Secondary influences: 0.6-0.8
# 4. Subtle accents: 0.3-0.5
# 5. Be specific (e.g., "Requinto Guitar" not just "Guitar")

STYLE_PRESETS = {
    "bachata-fusion": {
        "name": "Ethiopian Bachata Romántica",
        "description": "Romantic fusion of Ethiopian Tizita with Dominican Bachata",
        "prompts": [
            {"text": "Romantic Bachata", "weight": 1.0},
            {"text": "Ethiopian Tizita Modal Scales", "weight": 0.8},
            {"text": "Requinto Guitar Arpeggios", "weight": 0.7},
            {"text": "Soulful Melodic", "weight": 0.6},
            {"text": "Güira Rhythm", "weight": 0.5},
        ],
        "bpm": 95,
        "temperature": 0.9,
        "output_file": "exports/shega_lij_bachata_instrumental.wav",
    },
    "ethio-jazz": {
        "name": "Ethio-Jazz Fusion",
        "description": "Mulatu Astatke inspired Ethiopian Jazz",
        "prompts": [
            {"text": "Ethiopian Jazz", "weight": 1.0},
            {"text": "Vibraphon Melodic", "weight": 0.9},
            {"text": "African Rhythms", "weight": 0.8},
            {"text": "Brass Section", "weight": 0.7},
            {"text": "Groovy Bass", "weight": 0.6},
        ],
        "bpm": 110,
        "temperature": 0.85,
        "output_file": "exports/ethio_jazz_instrumental.wav",
    },
    "tizita-blues": {
        "name": "Tizita Blues",
        "description": "Ethiopian Tizita meets American Blues",
        "prompts": [
            {"text": "Blues Rock", "weight": 1.0},
            {"text": "Ethiopian Pentatonic Melody", "weight": 0.9},
            {"text": "Slide Guitar", "weight": 0.8},
            {"text": "Soulful Emotional", "weight": 0.7},
            {"text": "Minor Key Melancholy", "weight": 0.5},
        ],
        "bpm": 85,
        "temperature": 0.8,
        "output_file": "exports/tizita_blues_instrumental.wav",
    },
    "modern-ethiopian": {
        "name": "Modern Ethiopian Pop",
        "description": "Contemporary Ethiopian sound with modern production",
        "prompts": [
            {"text": "Ethiopian Pop", "weight": 1.0},
            {"text": "Modern Synth Pop", "weight": 0.8},
            {"text": "Krar Inspired Melody", "weight": 0.7},
            {"text": "Electronic Beats", "weight": 0.6},
            {"text": "Uplifting Energetic", "weight": 0.5},
        ],
        "bpm": 120,
        "temperature": 0.9,
        "output_file": "exports/modern_ethiopian_instrumental.wav",
    },
    "eskista-dance": {
        "name": "Eskista Dance Music",
        "description": "Traditional Ethiopian shoulder dance rhythm",
        "prompts": [
            {"text": "African Dance Music", "weight": 1.0},
            {"text": "Masinko Inspired", "weight": 0.9},
            {"text": "Percussive Rhythmic", "weight": 0.8},
            {"text": "Energetic Celebratory", "weight": 0.7},
            {"text": "Polyrhythmic", "weight": 0.6},
        ],
        "bpm": 130,
        "temperature": 0.95,
        "output_file": "exports/eskista_dance_instrumental.wav",
    },
}


def check_cached(output_path: Path, force: bool = False) -> bool:
    """Check if output already exists (caching)."""
    if force:
        return False
    if output_path.exists():
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"\n✅ Using cached file: {output_path}")
        print(f"   Size: {size_mb:.2f} MB")
        print("\n   💡 Use --force to regenerate")
        return True
    return False


async def generate_music(
    style_key: str = "bachata-fusion",
    duration: int = 30,
    force: bool = False,
) -> Path | None:
    """
    Generate Ethiopian fusion instrumental music using Lyria.

    Args:
        style_key: One of the STYLE_PRESETS keys
        duration: Duration in seconds (10-120)
        force: Regenerate even if cached

    Returns:
        Path to generated WAV file, or None if failed
    """
    preset = STYLE_PRESETS.get(style_key, STYLE_PRESETS["bachata-fusion"])
    output_path = Path(preset["output_file"])

    # Check cache
    if check_cached(output_path, force):
        return output_path

    print(f"🎵 {preset['name']}")
    print("=" * 55)
    print(f"   Description: {preset['description']}")
    print(f"   BPM: {preset['bpm']}")
    print(f"   Duration: {duration}s")
    print(f"   Temperature: {preset['temperature']}")
    print("=" * 55)

    # Show weighted prompts
    print("\n🎸 Weighted Prompts:")
    print("-" * 40)
    for p in preset["prompts"]:
        bar = "█" * int(p["weight"] * 10)
        print(f"   {p['weight']:.1f} {bar} {p['text']}")
    print("-" * 40)

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY not found in environment")
        print("   Set it in .env file or export GEMINI_API_KEY=...")
        return None

    # Lyria requires v1alpha API version
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})

    audio_chunks: list[bytes] = []
    capture_done = asyncio.Event()

    async def receive_audio(session):
        """Receive audio from Lyria stream in dedicated coroutine."""
        try:
            async for message in session.receive():
                if hasattr(message, "server_content") and message.server_content:
                    if hasattr(message.server_content, "audio_chunks"):
                        for chunk in message.server_content.audio_chunks:
                            if hasattr(chunk, "data") and chunk.data:
                                audio_chunks.append(chunk.data)
                                if len(audio_chunks) % 20 == 0:
                                    print(f"   📊 {len(audio_chunks)} chunks received...")
                await asyncio.sleep(0)
                if capture_done.is_set():
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"   ⚠️ Receive error: {e}")

    # Build weighted prompts
    weighted_prompts = [
        types.WeightedPrompt(text=p["text"], weight=p["weight"]) for p in preset["prompts"]
    ]

    print("\n▶ Generating instrumental...")

    try:
        async with client.aio.live.music.connect(model="models/lyria-realtime-exp") as session:
            print("   ✓ Connected to Lyria")

            # Start receiver task
            receive_task = asyncio.create_task(receive_audio(session))

            # Configure style
            await session.set_weighted_prompts(prompts=weighted_prompts)
            print(f"   ✓ Style configured: {preset['name']}")

            # Configure generation parameters
            await session.set_music_generation_config(
                config=types.LiveMusicGenerationConfig(
                    bpm=preset["bpm"],
                    temperature=preset["temperature"],
                )
            )
            print(f"   ✓ BPM: {preset['bpm']}, Temp: {preset['temperature']}")

            # Start streaming
            await session.play()
            print(f"   🎶 Streaming for {duration}s...")

            # Wait for duration
            await asyncio.sleep(duration)

            # Stop cleanly
            print(f"   ⏸ Stopping ({len(audio_chunks)} chunks)")
            capture_done.set()
            await session.stop()
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return None

    if not audio_chunks:
        print("\n❌ No audio received from Lyria")
        return None

    # Save as WAV (48kHz, 16-bit, stereo - Lyria's output format)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_data = b"".join(audio_chunks)
    with wave.open(str(output_path), "wb") as wav:
        wav.setnchannels(2)  # Stereo
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(48000)  # 48kHz
        wav.writeframes(audio_data)

    size_mb = len(audio_data) / 1024 / 1024

    print("\n" + "=" * 55)
    print("✅ GENERATED SUCCESSFULLY!")
    print("=" * 55)
    print(f"   📁 File: {output_path}")
    print(f"   📊 Size: {size_mb:.2f} MB")
    print(f"   ⏱️  Duration: {duration}s")
    print(f"   🎵 Style: {preset['name']}")
    print("\n   🎧 Enjoy your Ethiopian fusion instrumental!")

    return output_path


def list_styles():
    """Print available style presets."""
    print("\n🎵 Available Ethiopian Fusion Styles:")
    print("=" * 60)
    for key, preset in STYLE_PRESETS.items():
        print(f"\n   {key}")
        print(f"      {preset['name']}")
        print(f"      {preset['description']}")
        print(f"      BPM: {preset['bpm']}")
    print("\n" + "=" * 60)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate Ethiopian fusion instrumental music with Lyria",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python examples/lyria_example_ethiopian.py
  python examples/lyria_example_ethiopian.py --style ethio-jazz
  python examples/lyria_example_ethiopian.py --style tizita-blues --duration 45
  python examples/lyria_example_ethiopian.py --list-styles
  python examples/lyria_example_ethiopian.py --force
        """,
    )
    parser.add_argument(
        "--style",
        choices=list(STYLE_PRESETS.keys()),
        default="bachata-fusion",
        help="Music style preset (default: bachata-fusion)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration in seconds (10-120, default: 30)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if cached file exists",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available style presets",
    )

    args = parser.parse_args()

    if args.list_styles:
        list_styles()
        return

    await generate_music(
        style_key=args.style,
        duration=args.duration,
        force=args.force,
    )


if __name__ == "__main__":
    asyncio.run(main())
