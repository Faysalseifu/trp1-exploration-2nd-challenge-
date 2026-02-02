#!/usr/bin/env python3
"""
Example 08: Custom Provider

Demonstrates how to create and register a custom provider.
This is useful when you want to add support for new AI services.

Run:
    python examples/08_custom_provider.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.core.provider import MusicProvider
from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult


# Step 1: Define your custom provider class
@ProviderRegistry.register_music("my-custom-provider")
class MyCustomMusicProvider:
    """
    Example custom music provider.

    In a real implementation, this would call an actual API.
    """

    @property
    def name(self) -> str:
        return "my-custom-provider"

    @property
    def supports_vocals(self) -> bool:
        return True  # Or False for instrumental-only

    @property
    def supports_realtime(self) -> bool:
        return False  # True if supports streaming

    async def generate(
        self,
        prompt: str,
        *,
        bpm: int = 120,
        duration_seconds: int = 30,
        lyrics: str | None = None,
        reference_audio: str | None = None,
    ) -> GenerationResult:
        """
        Generate music using your custom API.

        Your implementation would:
        1. Prepare the request payload
        2. Call the external API
        3. Poll for completion (if async)
        4. Download the result
        5. Return GenerationResult
        """
        print(f"🎵 Custom Provider generating...")
        print(f"   Prompt: {prompt[:50]}...")
        print(f"   BPM: {bpm}, Duration: {duration_seconds}s")

        # Simulate API call
        await asyncio.sleep(1)

        # In real implementation, you would:
        # 1. Call your API
        # response = await self.client.post("/generate", json={...})
        #
        # 2. Poll for completion
        # while not complete:
        #     status = await self.client.get(f"/status/{task_id}")
        #     ...
        #
        # 3. Download result
        # await download_file(result_url, output_path)

        # For demo, return a mock result
        return GenerationResult(
            success=True,
            provider=self.name,
            content_type="music",
            file_path=None,  # Would be actual path
            metadata={
                "bpm": bpm,
                "duration": duration_seconds,
                "note": "This is a demo - no actual file generated",
            },
        )


async def demo_custom_provider():
    """Demonstrate using a custom provider."""

    print("🔧 Custom Provider Demo")
    print("=" * 60)

    # List all registered providers (including our custom one)
    print("\n📋 Registered Music Providers:")
    for name in ProviderRegistry.list_music():
        print(f"   • {name}")

    # Use our custom provider
    print("\n🎵 Using Custom Provider:")
    provider = ProviderRegistry.get_music("my-custom-provider")

    result = await provider.generate(
        prompt="A catchy pop melody",
        bpm=120,
        duration_seconds=15,
    )

    print(f"\n   Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   Provider: {result.provider}")
    print(f"   Metadata: {result.metadata}")

    print("\n" + "=" * 60)
    print("💡 To add your own provider:")
    print("   1. Create a class with @ProviderRegistry.register_music('name')")
    print("   2. Implement the MusicProvider protocol")
    print("   3. Import your module so the decorator runs")
    print("   4. Use ProviderRegistry.get_music('name') to get it")


if __name__ == "__main__":
    asyncio.run(demo_custom_provider())
