---
description: How to generate music with the AI content package
---

# Generate Music Workflow

## Prerequisites
- API key configured in `.env`: `GEMINI_API_KEY` or `AIMLAPI_KEY`
- `uv sync` completed

## Steps

// turbo-all

1. **Choose a provider and style**:
   ```bash
   # List available options
   uv run ai-content list-presets
   uv run ai-content list-providers
   ```

2. **Generate with preset**:
   ```bash
   uv run ai-content music --style jazz --provider lyria
   ```

3. **Generate with custom prompt**:
   ```bash
   uv run ai-content music \
     --prompt "Smooth jazz fusion with walking bass" \
     --provider lyria \
     --bpm 95 \
     --duration 30
   ```

4. **Generate with lyrics (MiniMax only)**:
   ```bash
   uv run ai-content music \
     --prompt "Pop ballad" \
     --provider minimax \
     --lyrics data/my_lyrics.txt
   ```

5. **Check output**:
   ```bash
   ls -la exports/
   ```

## Provider Comparison

| Provider | Vocals | Realtime | Reference Audio | Best For |
|----------|--------|----------|-----------------|----------|
| lyria | ❌ | ✅ | ❌ | Instrumentals, fast iteration |
| minimax | ✅ | ❌ | ✅ | Vocals, style transfer |
