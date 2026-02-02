"""Integrations module for external services."""

from ai_content.integrations.media import (
    MediaProcessor,
    check_ffmpeg_available,
)
from ai_content.integrations.archive import (
    ArchiveOrgSource,
    SourceMetadata,
)
from ai_content.integrations.youtube import (
    YouTubeUploader,
)

__all__ = [
    # Media processing
    "MediaProcessor",
    "check_ffmpeg_available",
    # Archive.org
    "ArchiveOrgSource",
    "SourceMetadata",
    # YouTube
    "YouTubeUploader",
]
