---
description: Skill for AI video generation with Veo and KlingAI
---

# Video Generation Skill

This skill enables AI-assisted video generation using multiple providers.

## Capabilities

- **Google Veo 3.1**: Fast generation, text-to-video and image-to-video
- **KlingAI v2.1**: Highest quality, slower (5-14 minutes)

## Provider Selection Matrix

| Need | Provider | Why |
|------|----------|-----|
| Quick preview | Veo | ~30 second generation |
| Highest quality | Kling | v2.1-master model |
| Vertical (9:16) | Either | Both support all aspects |
| Image animation | Either | Both support image-to-video |
| Budget-conscious | Veo | Typically cheaper |

## Prompt Engineering Patterns

### Scene Description Best Practices

```
[Subject][Action][Setting][Lighting][Camera][Style]
```

Example:
```
A majestic lion slowly walks through tall savanna grass,
golden hour sunlight casting long shadows,
cinematic slow motion with a tracking dolly shot,
nature documentary style, 8K resolution, shallow depth of field
```

### Camera Movement Keywords

| Effect | Keywords |
|--------|----------|
| Following subject | tracking shot, dolly, follow cam |
| Stable scene | static shot, locked off |
| Dramatic reveal | crane shot, push in |
| Smooth motion | steadicam, gimbal |
| First person | POV, first-person |

### Style Keywords

- Cinematic: film grain, anamorphic, color graded
- Documentary: natural lighting, handheld
- Commercial: pristine, studio lighting
- Artistic: stylized, abstract, surreal

## Common Issues

### "Generation timed out" (Kling)
- Normal for Kling (5-14 min)
- Check KLINGAI_API_KEY and KLINGAI_SECRET_KEY
- Verify JWT token generation

### "No video generated" (Veo)
- Check GEMINI_API_KEY
- Verify prompt doesn't violate content policy
- Try simpler prompt

## Integration Example

```python
from ai_content import ProviderRegistry
from ai_content.presets import get_video_preset

# Get preset
preset = get_video_preset("space")

# Get provider
provider = ProviderRegistry.get_video("veo")

# Generate
result = await provider.generate(
    prompt=preset.prompt,
    aspect_ratio=preset.aspect_ratio,
)

if result.success:
    print(f"Saved: {result.file_path}")
```

## Resources

- [AI_CONTENT_CREATION_GUIDELINES.md](../../docs/guides/AI_CONTENT_CREATION_GUIDELINES.md)
- Google Veo docs: https://ai.google.dev/gemini-api/docs/video
- KlingAI docs: https://docs.qingque.cn/
