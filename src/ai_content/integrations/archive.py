"""
Archive.org integration.

Search and fetch content from Archive.org for use as source material.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class SourceMetadata:
    """Metadata about an Archive.org item."""

    identifier: str
    title: str
    description: str = ""
    creator: str = ""
    date: str = ""
    thumbnail_url: str = ""
    media_urls: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def archive_url(self) -> str:
        """Direct link to Archive.org page."""
        return f"https://archive.org/details/{self.identifier}"


class ArchiveOrgSource:
    """
    Search and fetch from Archive.org.

    Archive.org provides free access to historical media including:
    - Audio recordings
    - Video clips
    - Images and photos

    Example:
        >>> source = ArchiveOrgSource()
        >>> results = await source.search("1930s jazz")
        >>> metadata = await source.get_metadata(results[0].identifier)
    """

    BASE_URL = "https://archive.org"
    API_URL = "https://archive.org/advancedsearch.php"
    METADATA_URL = "https://archive.org/metadata"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def search(
        self,
        query: str,
        *,
        media_type: str | None = None,
        limit: int = 10,
        sort: str = "downloads desc",
    ) -> list[SourceMetadata]:
        """
        Search Archive.org for content.

        Args:
            query: Search query
            media_type: Filter by type (audio, video, image, texts)
            limit: Maximum results
            sort: Sort order

        Returns:
            List of source metadata
        """
        logger.info(f"🔍 Searching Archive.org: {query}")

        # Build query
        q = query
        if media_type:
            q = f"{query} AND mediatype:{media_type}"

        params = {
            "q": q,
            "fl[]": ["identifier", "title", "description", "creator", "date"],
            "sort[]": sort,
            "rows": limit,
            "output": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.API_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            logger.error(f"Archive.org search failed: {e}")
            return []

        results = []
        for doc in data.get("response", {}).get("docs", []):
            identifier = doc.get("identifier", "")
            results.append(
                SourceMetadata(
                    identifier=identifier,
                    title=doc.get("title", ""),
                    description=doc.get("description", ""),
                    creator=doc.get("creator", ""),
                    date=doc.get("date", ""),
                    thumbnail_url=f"{self.BASE_URL}/services/img/{identifier}",
                )
            )

        logger.info(f"   Found {len(results)} results")
        return results

    async def get_metadata(self, identifier: str) -> SourceMetadata | None:
        """
        Get detailed metadata for an item.

        Args:
            identifier: Archive.org item identifier

        Returns:
            SourceMetadata with full details
        """
        logger.info(f"📦 Fetching metadata: {identifier}")

        url = f"{self.METADATA_URL}/{identifier}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            logger.error(f"Metadata fetch failed: {e}")
            return None

        metadata = data.get("metadata", {})
        files = data.get("files", [])

        # Extract media URLs
        media_urls = []
        for f in files:
            name = f.get("name", "")
            if any(name.endswith(ext) for ext in [".mp3", ".mp4", ".wav", ".ogg", ".jpg", ".png"]):
                media_urls.append(f"{self.BASE_URL}/download/{identifier}/{name}")

        return SourceMetadata(
            identifier=identifier,
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            creator=metadata.get("creator", ""),
            date=metadata.get("date", ""),
            thumbnail_url=f"{self.BASE_URL}/services/img/{identifier}",
            media_urls=media_urls,
            metadata=metadata,
        )

    async def get_thumbnail_url(self, identifier: str) -> str:
        """Get thumbnail URL for an item."""
        return f"{self.BASE_URL}/services/img/{identifier}"

    async def get_download_url(
        self,
        identifier: str,
        filename: str,
    ) -> str:
        """Get direct download URL for a file."""
        return f"{self.BASE_URL}/download/{identifier}/{filename}"
