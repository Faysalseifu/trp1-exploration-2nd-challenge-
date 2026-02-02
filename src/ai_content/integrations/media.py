"""
Media processing utilities.

Audio/video processing with FFmpeg for:
- Merging audio and video
- Format conversion
- Trimming and duration adjustments
"""

import asyncio
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ai_content.core.exceptions import ProviderError

logger = logging.getLogger(__name__)


def check_ffmpeg_available() -> bool:
    """Check if FFmpeg is available on the system."""
    return shutil.which("ffmpeg") is not None


class MediaProcessor:
    """
    Media processing using FFmpeg.

    Requires FFmpeg to be installed on the system.
    Install:
        - macOS: brew install ffmpeg
        - Ubuntu: apt install ffmpeg
        - Windows: choco install ffmpeg

    Example:
        >>> processor = MediaProcessor()
        >>> await processor.merge_audio_video(
        ...     audio_path=Path("music.wav"),
        ...     video_path=Path("video.mp4"),
        ...     output_path=Path("output.mp4"),
        ... )
    """

    def __init__(self, ffmpeg_path: str | None = None):
        self.ffmpeg_path = ffmpeg_path or shutil.which("ffmpeg") or "ffmpeg"

        if not check_ffmpeg_available():
            logger.warning("⚠️ FFmpeg not found. Media processing will fail.")

    async def merge_audio_video(
        self,
        audio_path: Path | str,
        video_path: Path | str,
        output_path: Path | str,
        *,
        audio_codec: str = "aac",
        video_codec: str = "copy",
        overwrite: bool = True,
    ) -> Path:
        """
        Merge audio and video into a single file.

        Args:
            audio_path: Path to audio file
            video_path: Path to video file
            output_path: Output file path
            audio_codec: Audio codec (default: aac)
            video_codec: Video codec (default: copy = no re-encoding)
            overwrite: Overwrite existing output

        Returns:
            Path to merged file

        Raises:
            ProviderError: If merge fails
        """
        audio_path = Path(audio_path)
        video_path = Path(video_path)
        output_path = Path(output_path)

        if not audio_path.exists():
            raise ProviderError("ffmpeg", f"Audio file not found: {audio_path}")
        if not video_path.exists():
            raise ProviderError("ffmpeg", f"Video file not found: {video_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_path,
            "-y" if overwrite else "-n",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-c:v",
            video_codec,
            "-c:a",
            audio_codec,
            "-shortest",  # End when shortest stream ends
            "-map",
            "0:v:0",  # Video from first input
            "-map",
            "1:a:0",  # Audio from second input
            str(output_path),
        ]

        logger.info(f"🔀 Merging: {video_path.name} + {audio_path.name}")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise ProviderError("ffmpeg", f"Merge failed: {error_msg}")

            logger.info(f"   ✅ Output: {output_path}")
            return output_path

        except FileNotFoundError:
            raise ProviderError("ffmpeg", "FFmpeg not found. Please install FFmpeg.")

    async def convert_format(
        self,
        input_path: Path | str,
        output_format: str,
        output_path: Path | str | None = None,
        *,
        overwrite: bool = True,
    ) -> Path:
        """
        Convert media to a different format.

        Args:
            input_path: Input file path
            output_format: Target format (e.g., "mp3", "mp4")
            output_path: Output path (auto-generated if not provided)
            overwrite: Overwrite existing file

        Returns:
            Path to converted file
        """
        input_path = Path(input_path)

        if output_path is None:
            output_path = input_path.with_suffix(f".{output_format}")
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_path,
            "-y" if overwrite else "-n",
            "-i",
            str(input_path),
            str(output_path),
        ]

        logger.info(f"🔄 Converting: {input_path.name} → {output_path.suffix}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise ProviderError("ffmpeg", f"Conversion failed: {error_msg}")

        return output_path

    async def trim(
        self,
        input_path: Path | str,
        output_path: Path | str,
        *,
        start_seconds: float = 0,
        duration_seconds: float | None = None,
        end_seconds: float | None = None,
    ) -> Path:
        """
        Trim media to specified duration.

        Args:
            input_path: Input file
            output_path: Output file
            start_seconds: Start time in seconds
            duration_seconds: Duration to keep
            end_seconds: End time (alternative to duration)

        Returns:
            Path to trimmed file
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss",
            str(start_seconds),
            "-i",
            str(input_path),
        ]

        if duration_seconds:
            cmd.extend(["-t", str(duration_seconds)])
        elif end_seconds:
            cmd.extend(["-to", str(end_seconds - start_seconds)])

        cmd.extend(["-c", "copy", str(output_path)])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

        if process.returncode != 0:
            raise ProviderError("ffmpeg", "Trim failed")

        return output_path

    async def get_duration(self, file_path: Path | str) -> float:
        """Get duration of media file in seconds."""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()

        try:
            return float(stdout.decode().strip())
        except ValueError:
            return 0.0
