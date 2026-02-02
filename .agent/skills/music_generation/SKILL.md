---
description: Skill for AI music generation with Lyria and MiniMax
---

# Music Generation Skill

This skill enables AI-assisted music generation using multiple providers.

## Capabilities

- **Google Lyria**: Real-time streaming, instrumental only
- **MiniMax Music 2.0**: Reference audio, lyrics with structure tags

## Provider Selection Matrix

| Need | Provider | Why |
|------|----------|-----|
| Fast iteration | Lyria | Real-time streaming |
| Vocals/singing | MiniMax | Lyria is instrumental only |
| Style transfer | MiniMax | Supports reference audio URL |
| Low latency | Lyria | No polling needed |

## Prompt Engineering Patterns

### Lyria (Weighted Prompts)
Lyria uses weighted prompts, not structure tags:

```python
prompt = """
[Smooth Jazz Fusion]
[Walking Bass Line, Brushed Drums]
[Warm Piano Chords, Vinyl Crackle]
Late night radio feel
"""
```

### MiniMax (Structure Tags for Lyrics)
Use structure tags for song sections:

```
[Intro]
(Soft piano)

[Verse 1]
Walking through the city lights
Finding my way home tonight

[Chorus]
This is where I belong
This is my song

[Outro]
(Fade out)
```

## Common Issues

### "No audio data received" (Lyria)
- Check GEMINI_API_KEY is set
- Verify quota hasn't been exceeded
- Try shorter duration

### "Rate limit exceeded" (MiniMax)
- Wait 60 seconds
- Check AIMLAPI_KEY is valid
- Consider using Lyria instead

## Integration Example

```python
from ai_content import ProviderRegistry
from ai_content.presets import get_music_preset

# Get preset
preset = get_music_preset("jazz")

# Get provider
provider = ProviderRegistry.get_music("lyria")

# Generate
result = await provider.generate(
    prompt=preset.prompt,
    bpm=preset.bpm,
    duration_seconds=30,
)

if result.success:
    print(f"Saved: {result.file_path}")
```

## Resources

- [AI_CONTENT_CREATION_GUIDELINES.md](../../docs/guides/AI_CONTENT_CREATION_GUIDELINES.md)
- Google Lyria docs: https://ai.google.dev/gemini-api/docs/audio
- AIMLAPI docs: https://docs.aimlapi.com/api-references/music-models
