# How to Extend the AI Content Package

This guide explains how to add new providers, presets, and features to the package.

## Adding a New Music Provider

### Step 1: Create the Provider File

Create `src/ai_content/providers/{your_provider}/__init__.py`:

```python
"""Your provider module."""
from ai_content.providers.your_provider.music import YourMusicProvider

__all__ = ["YourMusicProvider"]
```

Create `src/ai_content/providers/{your_provider}/music.py`:

```python
"""Your music provider implementation."""

import logging
from datetime import datetime, timezone
from pathlib import Path

from ai_content.core.registry import ProviderRegistry
from ai_content.core.result import GenerationResult
from ai_content.core.exceptions import ProviderError
from ai_content.config import get_settings

logger = logging.getLogger(__name__)


@ProviderRegistry.register_music("your_provider")
class YourMusicProvider:
    """
    Your music provider implementation.
    
    Features:
        - List key features here
    """
    
    # Required properties
    name = "your_provider"
    supports_vocals = True  # or False
    supports_realtime = False  # or True
    supports_reference_audio = False  # or True
    
    def __init__(self):
        # Initialize settings, clients, etc.
        self.settings = get_settings()
    
    async def generate(
        self,
        prompt: str,
        *,
        bpm: int = 120,
        duration_seconds: int = 30,
        lyrics: str | None = None,
        reference_audio_url: str | None = None,
        output_path: str | None = None,
    ) -> GenerationResult:
        """Generate music."""
        logger.info(f"🎵 {self.name}: Generating music")
        
        try:
            # Your implementation here
            # 1. Call the API
            # 2. Wait for completion (if async)
            # 3. Download/process result
            # 4. Save to file
            
            audio_data = b"..."  # Your audio bytes
            
            # Save
            if output_path:
                file_path = Path(output_path)
            else:
                output_dir = get_settings().output_dir
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                file_path = output_dir / f"{self.name}_{timestamp}.mp3"
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(audio_data)
            
            return GenerationResult(
                success=True,
                provider=self.name,
                content_type="music",
                file_path=file_path,
                data=audio_data,
                duration_seconds=duration_seconds,
                metadata={"prompt": prompt},
            )
        
        except Exception as e:
            logger.error(f"{self.name} generation failed: {e}")
            return GenerationResult(
                success=False,
                provider=self.name,
                content_type="music",
                error=str(e),
            )
```

### Step 2: Register the Provider

Import your module in `src/ai_content/providers/__init__.py`:

```python
from ai_content.providers import your_provider  # Add this line
```

### Step 3: Add Configuration (Optional)

If your provider needs configuration, add settings in `src/ai_content/config/settings.py`:

```python
class YourProviderSettings(BaseSettings):
    api_key: str = Field(default="", alias="YOUR_PROVIDER_API_KEY")
    base_url: str = "https://api.yourprovider.com"
    
    model_config = SettingsConfigDict(
        env_prefix="YOUR_PROVIDER_",
        extra="ignore",
    )

class Settings(BaseSettings):
    # ... existing settings ...
    your_provider: YourProviderSettings = Field(default_factory=YourProviderSettings)
```

### Step 4: Test Your Provider

Create `tests/unit/test_your_provider.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch

from ai_content.providers.your_provider import YourMusicProvider


@pytest.fixture
def provider():
    return YourMusicProvider()


@pytest.mark.asyncio
async def test_generate_success(provider):
    with patch.object(provider, '_call_api', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = b"fake audio data"
        
        result = await provider.generate("test prompt")
        
        assert result.success
        assert result.provider == "your_provider"
        assert result.content_type == "music"
```

---

## Adding a New Music Preset

### Step 1: Add to Presets Module

Edit `src/ai_content/presets/music.py`:

```python
# Add your preset
AFROBEATS = MusicPreset(
    name="afrobeats",
    prompt="""[Afrobeats]
[Talking Drums, Highlife Guitar]
[Shekere Percussion, Call and Response]
[Lagos Sound, Festival Energy]
Energetic West African vibes, Burna Boy inspired""",
    bpm=105,
    mood="energetic",
    tags=["afrobeats", "highlife", "african"],
)

# Add to the MUSIC_PRESETS dict
MUSIC_PRESETS: dict[str, MusicPreset] = {
    preset.name: preset
    for preset in [
        JAZZ, BLUES, ETHIOPIAN_JAZZ, CINEMATIC,
        ELECTRONIC, AMBIENT, LOFI, RNB,
        AFROBEATS,  # Add here
    ]
}
```

### Step 2: Export in __init__.py

Edit `src/ai_content/presets/__init__.py`:

```python
from ai_content.presets.music import (
    # ... existing imports ...
    AFROBEATS,  # Add this
)

__all__ = [
    # ... existing exports ...
    "AFROBEATS",  # Add this
]
```

---

## Adding a New CLI Command

Edit `src/ai_content/cli/main.py`:

```python
@app.command()
def your_command(
    arg1: str = typer.Option(..., "--arg1", help="Description"),
    flag: bool = typer.Option(False, "--flag", "-f", help="Flag description"),
):
    """Your command description."""
    asyncio.run(_your_async_function(arg1, flag))


async def _your_async_function(arg1: str, flag: bool):
    """Async implementation."""
    # Your implementation
    console.print("[green]Success![/green]")
```

---

## Best Practices Checklist

When adding new code:

- [ ] Use async/await for all I/O
- [ ] Full type hints on all functions
- [ ] Docstrings with Args, Returns, Example
- [ ] Return `GenerationResult` (don't raise for expected failures)
- [ ] Use structured logging with emoji prefix
- [ ] Add tests for success and failure paths
- [ ] Update CLI if user-facing
- [ ] Update README if public API changes
