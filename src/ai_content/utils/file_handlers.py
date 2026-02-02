"""
File handling utilities.

Download, upload, and manage content files.
"""

import asyncio
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

import httpx

from ai_content.core.exceptions import ProviderError

logger = logging.getLogger(__name__)


async def download_file(
    url: str,
    output_path: Path | str,
    *,
    timeout: float = 120.0,
    chunk_size: int = 8192,
) -> Path:
    """
    Download a file from URL.

    Args:
        url: Source URL
        output_path: Destination path
        timeout: Request timeout in seconds
        chunk_size: Download chunk size

    Returns:
        Path to downloaded file

    Raises:
        ProviderError: If download fails
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"📥 Downloading: {url[:50]}...")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        f.write(chunk)

        size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"   Downloaded: {output_path.name} ({size_mb:.2f} MB)")
        return output_path

    except httpx.HTTPError as e:
        raise ProviderError("download", f"Failed to download {url}: {e}")


async def download_to_bytes(
    url: str,
    *,
    timeout: float = 120.0,
) -> bytes:
    """
    Download a file to memory.

    Args:
        url: Source URL
        timeout: Request timeout

    Returns:
        File contents as bytes
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content


def generate_output_path(
    output_dir: Path | str,
    prefix: str,
    extension: str,
    *,
    timestamp: bool = True,
) -> Path:
    """
    Generate a unique output path.

    Args:
        output_dir: Output directory
        prefix: Filename prefix
        extension: File extension (with or without dot)
        timestamp: Whether to add timestamp

    Returns:
        Generated path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not extension.startswith("."):
        extension = f".{extension}"

    if timestamp:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{ts}{extension}"
    else:
        filename = f"{prefix}{extension}"

    return output_dir / filename


def ensure_dir(path: Path | str) -> Path:
    """Create directory if it doesn't exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_file(src: Path | str, dst: Path | str) -> Path:
    """Copy a file, creating destination directory if needed."""
    src = Path(src)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def get_file_size_mb(path: Path | str) -> float:
    """Get file size in megabytes."""
    return Path(path).stat().st_size / (1024 * 1024)


def cleanup_files(*paths: Path | str) -> None:
    """
    Delete files, ignoring errors.

    Useful for cleaning up temporary files.
    """
    for path in paths:
        try:
            path = Path(path)
            if path.exists():
                path.unlink()
                logger.debug(f"Cleaned up: {path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")


class TempFileManager:
    """
    Context manager for temporary files.

    Example:
        >>> async with TempFileManager() as temp:
        ...     path = temp.create("audio.wav")
        ...     # Use path...
        ... # Files auto-deleted on exit
    """

    def __init__(self, base_dir: Path | str | None = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            import tempfile

            self.base_dir = Path(tempfile.mkdtemp(prefix="ai_content_"))
        self.files: list[Path] = []

    def create(self, filename: str) -> Path:
        """Create a new temporary file path."""
        path = self.base_dir / filename
        self.files.append(path)
        return path

    async def __aenter__(self) -> "TempFileManager":
        self.base_dir.mkdir(parents=True, exist_ok=True)
        return self

    async def __aexit__(self, *args) -> None:
        for path in self.files:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

        try:
            if self.base_dir.exists():
                shutil.rmtree(self.base_dir)
        except Exception:
            pass
