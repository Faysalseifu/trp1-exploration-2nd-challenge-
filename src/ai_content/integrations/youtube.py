"""
YouTube upload integration.

Upload generated videos to YouTube using OAuth2 authentication.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class YouTubeUploader:
    """
    Upload videos to YouTube.

    Requires:
    1. Google Cloud Console project with YouTube Data API v3 enabled
    2. OAuth2 client credentials (client_secrets.json)
    3. User authorization (opens browser for consent)

    Setup:
        1. Go to console.cloud.google.com
        2. Create a project and enable YouTube Data API v3
        3. Create OAuth2 credentials (Desktop app)
        4. Download as client_secrets.json
        5. Place in .credentials/client_secrets.json

    Example:
        >>> uploader = YouTubeUploader()
        >>> await uploader.authenticate()
        >>> video_id = await uploader.upload(
        ...     video_path=Path("music_video.mp4"),
        ...     title="AI Generated Music Video",
        ...     description="Created with ai-content",
        ... )
    """

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(
        self,
        credentials_path: Path | str = ".credentials/client_secrets.json",
        token_path: Path | str = ".credentials/youtube_token.json",
    ):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.youtube = None
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate with YouTube API.

        Opens browser for OAuth consent if no saved token.

        Returns:
            True if authentication successful
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
        except ImportError:
            logger.error(
                "YouTube integration requires google-auth-oauthlib and google-api-python-client. "
                "Install with: pip install google-auth-oauthlib google-api-python-client"
            )
            return False

        creds = None

        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
            except Exception:
                pass

        # Get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request

                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    return False

                logger.info("🔐 Opening browser for YouTube authorization...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path),
                    self.SCOPES,
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as f:
                f.write(creds.to_json())

        self.youtube = build("youtube", "v3", credentials=creds)
        self._authenticated = True
        logger.info("✅ YouTube authenticated")
        return True

    async def upload(
        self,
        video_path: Path | str,
        title: str,
        description: str = "",
        *,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "unlisted",
        tags: list[str] | None = None,
    ) -> str:
        """
        Upload video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            category_id: YouTube category ID
            privacy_status: "public", "unlisted", or "private"
            tags: Optional list of tags

        Returns:
            YouTube video ID

        Raises:
            RuntimeError: If not authenticated or upload fails
        """
        if not self._authenticated:
            success = await self.authenticate()
            if not success:
                raise RuntimeError("YouTube authentication failed")

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError:
            raise RuntimeError("google-api-python-client not installed")

        logger.info(f"📤 Uploading to YouTube: {video_path.name}")

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
            },
        }

        if tags:
            body["snippet"]["tags"] = tags

        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,
            resumable=True,
        )

        # This is synchronous, but we're wrapping it
        import asyncio

        def do_upload():
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )
            response = request.execute()
            return response.get("id")

        video_id = await asyncio.get_event_loop().run_in_executor(None, do_upload)

        logger.info(f"✅ Uploaded: https://youtube.com/watch?v={video_id}")
        return video_id

    def get_video_url(self, video_id: str) -> str:
        """Get YouTube video URL from ID."""
        return f"https://www.youtube.com/watch?v={video_id}"
