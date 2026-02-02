---
description: How to generate video with the AI content package
---

# Generate Video Workflow

## Prerequisites
- API key configured in `.env`: `GEMINI_API_KEY` or `KLINGAI_API_KEY` + `KLINGAI_SECRET_KEY`
- `uv sync` completed

## Steps

// turbo-all

1. **Generate with preset**:
   ```bash
   uv run ai-content video --style nature --provider veo
   ```

2. **Generate with custom prompt**:
   ```bash
   uv run ai-content video \
     --prompt "Dragon soaring over mountains at sunset, cinematic, 8K" \
     --provider veo \
     --aspect 16:9
   ```

3. **Generate with KlingAI (higher quality, 5-14 min)**:
   ```bash
   uv run ai-content video \
     --prompt "Epic fantasy scene" \
     --provider kling \
     --aspect 16:9
   ```

4. **Check output**:
   ```bash
   ls -la exports/*.mp4
   ```

## Provider Comparison

| Provider | Quality | Speed | Image-to-Video | Best For |
|----------|---------|-------|----------------|----------|
| veo | Good | Fast (~30s) | ✅ | Quick iterations |
| kling | Highest | Slow (5-14min) | ✅ | Final renders |
