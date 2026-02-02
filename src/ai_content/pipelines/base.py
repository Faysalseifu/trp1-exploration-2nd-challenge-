"""
Base pipeline abstractions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai_content.core.result import GenerationResult


@dataclass
class PipelineResult:
    """
    Result of a pipeline execution.

    Aggregates multiple generation results with timing and error info.
    """

    success: bool
    outputs: dict[str, GenerationResult] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """Calculate pipeline duration."""
        if self.completed_at is None:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def output_files(self) -> list[Path]:
        """Get all output file paths."""
        return [
            output.file_path
            for output in self.outputs.values()
            if output.file_path and output.file_path.exists()
        ]

    def add_output(self, key: str, result: GenerationResult) -> None:
        """Add an output result."""
        self.outputs[key] = result
        if not result.success and result.error:
            self.errors.append(f"{key}: {result.error}")

    def complete(self, success: bool | None = None) -> "PipelineResult":
        """Mark pipeline as completed."""
        self.completed_at = datetime.now(timezone.utc)
        if success is not None:
            self.success = success
        elif self.success and self.errors:
            self.success = False
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "outputs": {
                k: {
                    "success": v.success,
                    "provider": v.provider,
                    "file_path": str(v.file_path) if v.file_path else None,
                    "error": v.error,
                }
                for k, v in self.outputs.items()
            },
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


@dataclass
class PipelineConfig:
    """
    Configuration for pipeline execution.
    """

    output_dir: Path = field(default_factory=lambda: Path("exports"))
    parallel: bool = True
    stop_on_error: bool = False
    cleanup_on_failure: bool = True

    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
