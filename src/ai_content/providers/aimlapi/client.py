"""
AIMLAPI base client.

Shared HTTP client for all AIMLAPI-based providers.
"""

import asyncio
import logging
from typing import Any

import httpx

from ai_content.core.exceptions import (
    ProviderError,
    RateLimitError,
    AuthenticationError,
)
from ai_content.config import get_settings

logger = logging.getLogger(__name__)

APPLICATION_JSON = "application/json"


class AIMLAPIClient:
    """
    Base HTTP client for AIMLAPI.

    Provides shared functionality for all AIMLAPI-based providers:
    - Authentication header management
    - Request/response handling
    - Polling for async operations
    - Error handling

    Example:
        >>> client = AIMLAPIClient()
        >>> result = await client.submit_generation(
        ...     "/v2/generate/audio",
        ...     {"model": "minimax/music-2.0", "prompt": "jazz"}
        ... )
    """

    def __init__(self):
        self.settings = get_settings().aimlapi
        self._http_client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Get authorization headers."""
        if not self.settings.api_key:
            raise AuthenticationError("aimlapi")
        return {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": APPLICATION_JSON,
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=self.settings.base_url,
                timeout=float(self.settings.request_timeout),
                headers=self.headers,
            )
        return self._http_client

    async def close(self):
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    async def submit_generation(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Submit a generation request.

        Args:
            endpoint: API endpoint (e.g., "/v2/generate/audio")
            payload: Request payload

        Returns:
            Response JSON containing generation ID
        """
        client = await self._get_client()

        try:
            response = await client.post(endpoint, json=payload)
            self._handle_error(response)
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_error(e.response)
            raise

    async def poll_status(
        self,
        endpoint: str,
        generation_id: str,
    ) -> dict[str, Any]:
        """
        Poll for generation status.

        Args:
            endpoint: API endpoint
            generation_id: ID from submit_generation

        Returns:
            Status response
        """
        client = await self._get_client()

        response = await client.get(
            endpoint,
            params={"generation_id": generation_id},
        )
        self._handle_error(response)
        return response.json()

    async def wait_for_completion(
        self,
        endpoint: str,
        generation_id: str,
        check_complete: callable = None,
    ) -> dict[str, Any]:
        """
        Poll until generation is complete.

        Args:
            endpoint: API endpoint for status checks
            generation_id: ID from submit_generation
            check_complete: Optional function to check if complete

        Returns:
            Final status response
        """
        logger.info(f"   Polling for completion (ID: {generation_id[:8]}...)")

        for attempt in range(self.settings.max_poll_attempts):
            status = await self.poll_status(endpoint, generation_id)

            # Default completion check
            if check_complete:
                is_complete = check_complete(status)
            else:
                state = status.get("status") or status.get("state", "")
                is_complete = state.lower() in ("completed", "done", "success")
                is_failed = state.lower() in ("failed", "error")

                if is_failed:
                    error = (
                        status.get("error")
                        or status.get("message")
                        or "Generation failed"
                    )
                    raise ProviderError("aimlapi", error)

            if is_complete:
                logger.info(f"   Completed after {attempt + 1} polls")
                return status

            logger.debug(f"   Poll {attempt + 1}/{self.settings.max_poll_attempts}")
            await asyncio.sleep(self.settings.poll_interval)

        raise ProviderError(
            "aimlapi",
            f"Generation timed out after {self.settings.max_poll_attempts} polls",
        )

    async def download_file(self, url: str) -> bytes:
        """Download file from URL."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    def _handle_error(self, response: httpx.Response):
        """Handle HTTP errors."""
        if response.status_code == 401:
            raise AuthenticationError("aimlapi")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError("aimlapi", int(retry_after) if retry_after else None)
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = (
                    error_data.get("error")
                    or error_data.get("message")
                    or str(error_data)
                )
            except Exception:
                message = response.text[:200]
            raise ProviderError("aimlapi", message)
