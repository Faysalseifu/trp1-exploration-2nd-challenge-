"""
Generation result container.

Provides a unified result type for all generation operations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class GenerationResult:
    """
    Result container for content generation operations.

    Attributes:
        success: Whether generation completed successfully
        provider: Name of the provider that generated the content
        content_type: Type of content ("music", "video", "image")
        file_path: Path to saved file (if saved)
        data: Raw bytes of generated content (if not saved)
        duration_seconds: Duration of audio/video content
        metadata: Provider-specific metadata
        error: Error message if generation failed
        generation_id: Provider's unique ID for this generation
        created_at: Timestamp of generation

    Example:
        >>> result = await provider.generate("jazz fusion")
        >>> if result.success:
        ...     print(f"Saved to: {result.file_path}")
        ... else:
        ...     print(f"Error: {result.error}")
    """

    success: bool
    provider: str
    content_type: str  # "music", "video", "image"

    file_path: Path | None = None
    data: bytes | None = None
    duration_seconds: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    generation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def save(self, path: str | Path) -> Path:
        """
        Save content to a file.

        Args:
            path: Destination file path

        Returns:
            Path to saved file

        Raises:
            ValueError: If no data available to save
        """
        if self.data is None:
            if self.file_path and self.file_path.exists():
                # Already saved, copy to new location
                import shutil

                dest = Path(path)
                shutil.copy(self.file_path, dest)
                return dest
            raise ValueError("No data available to save")

        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.data)
        self.file_path = dest
        return dest

    @property
    def file_size_mb(self) -> float | None:
        """Get file size in megabytes."""
        if self.file_path and self.file_path.exists():
            return self.file_path.stat().st_size / (1024 * 1024)
        if self.data:
            return len(self.data) / (1024 * 1024)
        return None

    def __repr__(self) -> str:
        status = "✅" if self.success else "❌"
        size = f"{self.file_size_mb:.2f}MB" if self.file_size_mb else "no data"
        return f"GenerationResult({status} {self.provider}/{self.content_type}, {size})"


@dataclass
class PollingResult:
    """
    Result of a polling operation for async generation.

    Used internally by providers that require polling for completion.
    """

    status: str  # "pending", "processing", "completed", "failed"
    progress: float = 0.0  # 0.0 to 1.0
    result_url: str | None = None
    error: str | None = None

    @property
    def is_complete(self) -> bool:
        return self.status in ("completed", "failed")

    @property
    def is_success(self) -> bool:
        return self.status == "completed"
