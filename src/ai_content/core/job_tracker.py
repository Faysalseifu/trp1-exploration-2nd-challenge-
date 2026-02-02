"""
Job Tracker for AI Content Generation.

Persistent SQLite-based tracking for generation jobs to:
- Prevent duplicate API calls
- Track job status (queued, processing, completed, failed, downloaded)
- Provide history and statistics
- Enable recovery of pending jobs
"""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class JobStatus(str, Enum):
    """Job status states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    DOWNLOADED = "downloaded"
    FAILED = "failed"


@dataclass
class Job:
    """Represents a generation job."""

    id: str  # generation_id from API
    provider: str
    content_type: str
    prompt_hash: str
    prompt: str
    command: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    output_path: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Job":
        """Create Job from database row."""
        return cls(
            id=row["id"],
            provider=row["provider"],
            content_type=row["content_type"],
            prompt_hash=row["prompt_hash"],
            prompt=row["prompt"],
            command=row["command"],
            status=JobStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            output_path=row["output_path"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
        )


class JobTracker:
    """
    SQLite-based job tracker for AI generation requests.

    Stores jobs in ~/.ai-content/jobs.db by default.

    Example:
        >>> tracker = JobTracker()
        >>> job = tracker.create_job(
        ...     generation_id="abc123",
        ...     provider="minimax",
        ...     content_type="music",
        ...     prompt="Bachata beat",
        ...     command="uv run ai-content music ...",
        ... )
        >>> tracker.update_status("abc123", JobStatus.COMPLETED, output_path="song.mp3")
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        provider TEXT NOT NULL,
        content_type TEXT NOT NULL,
        prompt_hash TEXT NOT NULL,
        prompt TEXT NOT NULL,
        command TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        output_path TEXT,
        metadata TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_prompt_hash ON jobs(prompt_hash);
    CREATE INDEX IF NOT EXISTS idx_status ON jobs(status);
    CREATE INDEX IF NOT EXISTS idx_provider ON jobs(provider);
    CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at);
    """

    def __init__(self, db_path: Path | None = None):
        """
        Initialize the job tracker.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.ai-content/jobs.db
        """
        if db_path is None:
            db_path = Path.home() / ".ai-content" / "jobs.db"
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)

    @contextmanager
    def _get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def hash_prompt(
        prompt: str,
        provider: str,
        content_type: str,
        lyrics: str | None = None,
        reference_url: str | None = None,
    ) -> str:
        """
        Create a hash for duplicate detection.

        Combines prompt, provider, content type, and optional lyrics/reference
        to create a unique fingerprint.
        """
        parts = [prompt, provider, content_type]
        if lyrics:
            parts.append(lyrics)
        if reference_url:
            parts.append(reference_url)
        combined = "|".join(parts)
        return hashlib.md5(combined.encode()).hexdigest()

    def create_job(
        self,
        generation_id: str,
        provider: str,
        content_type: str,
        prompt: str,
        command: str,
        lyrics: str | None = None,
        reference_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Job:
        """
        Create a new job record.

        Args:
            generation_id: ID from the API response
            provider: Provider name (minimax, lyria, etc.)
            content_type: Content type (music, video, image)
            prompt: The generation prompt
            command: Full CLI command for reference
            lyrics: Optional lyrics content
            reference_url: Optional reference audio URL
            metadata: Additional metadata (bpm, duration, etc.)

        Returns:
            The created Job object
        """
        now = datetime.now(timezone.utc).isoformat()
        prompt_hash = self.hash_prompt(prompt, provider, content_type, lyrics, reference_url)

        # Include lyrics in metadata if provided
        if metadata is None:
            metadata = {}
        if lyrics:
            metadata["has_lyrics"] = True
            metadata["lyrics_length"] = len(lyrics)
        if reference_url:
            metadata["reference_url"] = reference_url

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO jobs (
                    id, provider, content_type, prompt_hash, prompt,
                    command, status, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    generation_id,
                    provider,
                    content_type,
                    prompt_hash,
                    prompt,
                    command,
                    JobStatus.QUEUED.value,
                    now,
                    now,
                    json.dumps(metadata) if metadata else None,
                ),
            )

        return Job(
            id=generation_id,
            provider=provider,
            content_type=content_type,
            prompt_hash=prompt_hash,
            prompt=prompt,
            command=command,
            status=JobStatus.QUEUED,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
            metadata=metadata,
        )

    def get_job(self, job_id: str) -> Job | None:
        """Get a job by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return Job.from_row(row) if row else None

    def find_duplicate(
        self,
        prompt: str,
        provider: str,
        content_type: str,
        lyrics: str | None = None,
        reference_url: str | None = None,
    ) -> Job | None:
        """
        Find an existing job with the same prompt hash.

        Returns the most recent matching job, or None if no duplicate exists.
        Only returns jobs that are not failed.
        """
        prompt_hash = self.hash_prompt(prompt, provider, content_type, lyrics, reference_url)

        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM jobs
                WHERE prompt_hash = ? AND status != ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (prompt_hash, JobStatus.FAILED.value),
            ).fetchone()
            return Job.from_row(row) if row else None

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        output_path: str | None = None,
    ) -> bool:
        """
        Update job status.

        Args:
            job_id: The job ID
            status: New status
            output_path: Output file path (for completed/downloaded)

        Returns:
            True if job was found and updated
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            if output_path:
                cursor = conn.execute(
                    """
                    UPDATE jobs
                    SET status = ?, updated_at = ?, output_path = ?
                    WHERE id = ?
                    """,
                    (status.value, now, output_path, job_id),
                )
            else:
                cursor = conn.execute(
                    """
                    UPDATE jobs
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status.value, now, job_id),
                )
            return cursor.rowcount > 0

    def list_jobs(
        self,
        status: JobStatus | None = None,
        provider: str | None = None,
        content_type: str | None = None,
        limit: int = 50,
    ) -> list[Job]:
        """
        List jobs with optional filters.

        Args:
            status: Filter by status
            provider: Filter by provider
            content_type: Filter by content type
            limit: Maximum number of results

        Returns:
            List of matching jobs, most recent first
        """
        query = "SELECT * FROM jobs WHERE 1=1"
        params: list[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status.value)
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        if content_type:
            query += " AND content_type = ?"
            params.append(content_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Job.from_row(row) for row in rows]

    def get_stats(self) -> dict[str, Any]:
        """
        Get aggregate statistics.

        Returns:
            Dictionary with job counts by status and provider
        """
        with self._get_connection() as conn:
            # Total count
            total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

            # Count by status
            status_counts = {}
            for status in JobStatus:
                count = conn.execute(
                    "SELECT COUNT(*) FROM jobs WHERE status = ?",
                    (status.value,),
                ).fetchone()[0]
                status_counts[status.value] = count

            # Count by provider
            provider_rows = conn.execute(
                """
                SELECT provider, COUNT(*) as count
                FROM jobs
                GROUP BY provider
                ORDER BY count DESC
                """
            ).fetchall()
            provider_counts = {row["provider"]: row["count"] for row in provider_rows}

            # Count by content type
            type_rows = conn.execute(
                """
                SELECT content_type, COUNT(*) as count
                FROM jobs
                GROUP BY content_type
                ORDER BY count DESC
                """
            ).fetchall()
            type_counts = {row["content_type"]: row["count"] for row in type_rows}

            # Recent activity (last 24h)
            yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
            recent = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE created_at >= ?",
                (yesterday,),
            ).fetchone()[0]

            return {
                "total": total,
                "by_status": status_counts,
                "by_provider": provider_counts,
                "by_type": type_counts,
                "recent_24h": recent,
            }

    def get_pending_jobs(self) -> list[Job]:
        """Get all jobs that are still pending (queued or processing)."""
        return self.list_jobs(status=JobStatus.QUEUED) + self.list_jobs(status=JobStatus.PROCESSING)


# Global instance for convenience
_tracker: JobTracker | None = None


def get_tracker() -> JobTracker:
    """Get or create the global job tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = JobTracker()
    return _tracker
