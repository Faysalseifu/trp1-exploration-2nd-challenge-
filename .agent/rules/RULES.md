# AI Content Package Development Rules

These rules govern AI agent behavior when developing, extending, or maintaining the `ai_content` package.

---

## Core Principles

### 1. Async-First Architecture
All I/O operations MUST be async:

```python
# ✅ Correct
async def generate(self, prompt: str) -> GenerationResult:
    async with httpx.AsyncClient() as client:
        response = await client.post(...)

# ❌ Wrong
def generate(self, prompt: str) -> GenerationResult:
    response = requests.post(...)  # Blocking!
```

### 2. Type Safety with Protocols
Use Python Protocols for interfaces (structural subtyping):

```python
# ✅ Correct - Protocol + @runtime_checkable
@runtime_checkable
class MusicProvider(Protocol):
    @property
    def name(self) -> str: ...
    
    async def generate(self, prompt: str, **kwargs) -> GenerationResult: ...

# ❌ Wrong - ABC inheritance
class MusicProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> GenerationResult: ...
```

### 3. Registry Pattern for Providers
All providers MUST register via decorator:

```python
# ✅ Correct
@ProviderRegistry.register_music("my_provider")
class MyMusicProvider:
    name = "my_provider"
    supports_vocals = True
    ...

# ❌ Wrong - Manual registration
ProviderRegistry._music_providers["my_provider"] = MyMusicProvider
```

### 4. Result Objects Over Exceptions
Use `GenerationResult` with `success=False` for expected failures:

```python
# ✅ Correct
async def generate(...) -> GenerationResult:
    try:
        ...
    except RateLimitError:
        return GenerationResult(
            success=False,
            provider=self.name,
            content_type="music",
            error="Rate limit exceeded",
        )

# ❌ Wrong - Raising for expected conditions
async def generate(...) -> GenerationResult:
    ...
    raise GenerationException("Rate limit exceeded")
```

### 5. Pydantic for Configuration
All settings use Pydantic models:

```python
# ✅ Correct
from pydantic_settings import BaseSettings

class MySettings(BaseSettings):
    api_key: str = Field(default="", alias="MY_API_KEY")
    timeout: int = 30

# ❌ Wrong - Raw dicts or dataclasses
config = {"api_key": os.environ.get("MY_API_KEY")}
```

---

## Provider Implementation Checklist

When implementing a new provider:

- [ ] Create file in `src/ai_content/providers/{category}/{provider_name}.py`
- [ ] Implement the appropriate Protocol (`MusicProvider`, `VideoProvider`, `ImageProvider`)
- [ ] Add `@ProviderRegistry.register_{type}("{name}")` decorator
- [ ] Add property flags: `name`, `supports_*`
- [ ] Implement `async def generate(...)` with proper signature
- [ ] Return `GenerationResult` for all outcomes (success and failure)
- [ ] Add settings class if provider needs configuration
- [ ] Import in `providers/{category}/__init__.py` to trigger registration
- [ ] Add tests in `tests/unit/test_providers.py`
- [ ] Update CLI if new flags needed

---

## Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Provider Class | `{Provider}{Type}Provider` | `GoogleLyriaProvider` |
| Settings Class | `{Provider}Settings` | `GoogleSettings` |
| Registry Name | lowercase, hyphen-free | `"lyria"`, `"minimax"` |
| Preset Names | lowercase, hyphen-separated | `"ethiopian-jazz"` |

---

## Datetime Handling

Always use timezone-aware UTC:

```python
# ✅ Correct
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)

# ❌ Wrong - Naive datetime
created_at = datetime.utcnow()  # Deprecated!
created_at = datetime.now()     # Not timezone-aware
```

---

## Logging Standards

Use structured logging with context:

```python
import logging
logger = logging.getLogger(__name__)

# ✅ Correct
logger.info(f"🎵 {self.name}: Generating {duration}s at {bpm} BPM")
logger.debug(f"   Prompt: {prompt[:50]}...")
logger.error(f"{self.name} generation failed: {e}")

# ❌ Wrong - No context, no emoji for visual scanning
logger.info("generating music")
```

---

## Error Handling

Use custom exceptions from `ai_content.core.exceptions`:

| Exception | When to Use |
|-----------|-------------|
| `ProviderError` | General provider failures |
| `RateLimitError` | Rate limit exceeded (include `retry_after`) |
| `AuthenticationError` | API key invalid/missing |
| `GenerationError` | Content generation failed |
| `TimeoutError` | Operation timed out |
| `ConfigurationError` | Invalid or missing config |

---

## Testing Rules

1. **Unit tests** never hit real APIs
2. Use `pytest-asyncio` for async tests
3. Mock provider clients with `unittest.mock`
4. Test both success and failure paths
5. Cover edge cases with property-based tests (Hypothesis)

```python
@pytest.mark.asyncio
async def test_lyria_generate_success(mock_client):
    provider = GoogleLyriaProvider()
    result = await provider.generate("jazz", duration_seconds=10)
    assert result.success
    assert result.provider == "lyria"
```

---

## File Organization

```
src/ai_content/
├── core/           # Abstractions (don't import providers here)
├── config/         # Settings (don't import providers here)
├── providers/      # Implementations (import core, config)
├── presets/        # Static data (no external imports)
├── pipelines/      # Orchestration (import everything)
├── utils/          # Shared utilities
└── cli/            # User interface (import everything)
```

**Import Direction**: `cli` → `pipelines` → `providers` → `core` + `config`

---

## Documentation Requirements

Every public API must have:

1. **Docstring** with Args, Returns, Raises, Example
2. **Type hints** for all parameters and returns
3. **Example usage** in docstring

```python
async def generate(
    self,
    prompt: str,
    *,
    bpm: int = 120,
    duration_seconds: int = 30,
) -> GenerationResult:
    """
    Generate music from a text prompt.
    
    Args:
        prompt: Text description of the music style
        bpm: Beats per minute (tempo)
        duration_seconds: Length of generated audio
        
    Returns:
        GenerationResult containing audio data or file path
        
    Raises:
        AuthenticationError: If API key is invalid
        
    Example:
        >>> result = await provider.generate("smooth jazz", bpm=95)
        >>> result.save("output.wav")
    """
```
