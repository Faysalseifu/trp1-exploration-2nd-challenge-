"""
Custom exceptions for the AI content package.
"""


class AIContentError(Exception):
    """Base exception for all AI content errors."""

    pass


class ProviderError(AIContentError):
    """Error from a content provider."""

    def __init__(self, provider: str, message: str, cause: Exception | None = None):
        self.provider = provider
        self.cause = cause
        super().__init__(f"[{provider}] {message}")


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""

    def __init__(self, provider: str, retry_after: int | None = None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after}s"
        super().__init__(provider, message)


class AuthenticationError(ProviderError):
    """Authentication failed with provider."""

    def __init__(self, provider: str):
        super().__init__(provider, "Authentication failed. Check API key.")


class GenerationError(ProviderError):
    """Content generation failed."""

    pass


class TimeoutError(ProviderError):
    """Operation timed out."""

    def __init__(self, provider: str, operation: str, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        super().__init__(provider, f"{operation} timed out after {timeout_seconds}s")


class ConfigurationError(AIContentError):
    """Configuration is invalid or missing."""

    pass


class UnsupportedOperationError(AIContentError):
    """Requested operation not supported by provider."""

    def __init__(self, provider: str, operation: str):
        self.provider = provider
        self.operation = operation
        super().__init__(
            f"Provider '{provider}' does not support operation: {operation}"
        )
