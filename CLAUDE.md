# AI Content Generator - Agent Rules

> This file contains rules for AI agents working on this codebase.
> For full development rules, see [.agent/rules/RULES.md](.agent/rules/RULES.md)

## Quick Reference

### Package Structure
```
src/ai_content/
├── core/           # Protocols, Registry, Result, Exceptions
├── config/         # Pydantic Settings
├── providers/      # Provider implementations (Google, AIMLAPI, Kling)
├── presets/        # Music and video style presets
├── pipelines/      # Orchestration (future)
└── cli/            # Typer CLI
```

### Import Chain
`cli` → `pipelines` → `providers` → `core` + `config`

### Key Rules

1. **Async-First**: All I/O must be async
2. **Protocols**: Use `Protocol` over ABC for interfaces
3. **Registry Pattern**: Providers register via `@ProviderRegistry.register_*` decorators
4. **Result Objects**: Return `GenerationResult`, don't raise for expected failures
5. **Type Safety**: Full type hints, use Pydantic for config
6. **UTC Datetimes**: `datetime.now(timezone.utc)`, never `utcnow()`

### Adding a Provider

```python
@ProviderRegistry.register_music("new_provider")
class NewMusicProvider:
    name = "new_provider"
    supports_vocals = True
    supports_realtime = False
    supports_reference_audio = False
    
    async def generate(self, prompt: str, **kwargs) -> GenerationResult:
        ...
```

### Skills Available

- `/generate-music` - Music generation workflow
- `/generate-video` - Video generation workflow
- Music Generation Skill - Provider selection, prompt patterns
- Video Generation Skill - Camera keywords, style patterns
- Prompt Engineering Skill - Best practices, anti-patterns

### Documentation

- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Extending Guide](docs/guides/EXTENDING.md)
- [Content Guidelines](docs/guides/AI_CONTENT_CREATION_GUIDELINES.md)
- [Full Rules](.agent/rules/RULES.md)
