#!/usr/bin/env python3
"""
Example 07: Archive.org Integration

Search Archive.org for source material and use it for content generation.

Run:
    python examples/07_archive_integration.py

    # Custom search
    python examples/07_archive_integration.py "1950s jazz"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content.integrations.archive import ArchiveOrgSource


async def search_archive(query: str = "1930s jazz recordings"):
    """Search Archive.org for content."""

    print("🔍 Archive.org Integration Demo")
    print("=" * 60)
    print(f"   Query: {query}")
    print("=" * 60)

    source = ArchiveOrgSource()

    # Search
    print("\n📚 Searching...")
    results = await source.search(query, media_type="audio", limit=5)

    if not results:
        print("   No results found")
        return

    print(f"\n   Found {len(results)} results:\n")

    for i, item in enumerate(results, 1):
        print(f"   {i}. {item.title[:50]}")
        print(f"      ID: {item.identifier}")
        print(f"      Creator: {item.creator or 'Unknown'}")
        print(f"      URL: {item.archive_url}")
        print()

    # Get detailed metadata for first result
    print("-" * 40)
    print(f"\n📦 Fetching details for: {results[0].identifier}")

    metadata = await source.get_metadata(results[0].identifier)

    if metadata:
        print(f"   Title: {metadata.title}")
        print(
            f"   Description: {metadata.description[:100]}..."
            if metadata.description
            else "   Description: N/A"
        )
        print(f"   Thumbnail: {metadata.thumbnail_url}")

        if metadata.media_urls:
            print(f"\n   Available media files ({len(metadata.media_urls)}):")
            for url in metadata.media_urls[:3]:
                print(f"      → {url.split('/')[-1]}")

    print("\n💡 Use these URLs as source material for content generation!")
    print("   Example: Use thumbnail as keyframe for video generation")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "1930s jazz recordings"
    asyncio.run(search_archive(query))
