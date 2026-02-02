"""Core module exports."""

from ai_content.core.provider import (
    MusicProvider,
    VideoProvider,
    ImageProvider,
)
from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult, PollingResult
from ai_content.core.exceptions import (
    AIContentError,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    GenerationError,
    TimeoutError,
    ConfigurationError,
    UnsupportedOperationError,
)
from ai_content.core.job_tracker import (
    JobTracker,
    Job,
    JobStatus,
    get_tracker,
)

__all__ = [
    # Protocols
    "MusicProvider",
    "VideoProvider",
    "ImageProvider",
    # Registry
    "ProviderRegistry",
    # Results
    "GenerationResult",
    "PollingResult",
    # Job Tracking
    "JobTracker",
    "Job",
    "JobStatus",
    "get_tracker",
    # Exceptions
    "AIContentError",
    "ProviderError",
    "RateLimitError",
    "AuthenticationError",
    "GenerationError",
    "TimeoutError",
    "ConfigurationError",
    "UnsupportedOperationError",
]
