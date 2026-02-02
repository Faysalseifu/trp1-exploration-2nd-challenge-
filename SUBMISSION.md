# Part 2: Codebase Exploration

## Verification Commands

### Providers

```
$ uv run -- python -m ai_content.cli.main list-providers
<frozen runpy>:128: RuntimeWarning: 'ai_content.cli.main' found in sys.modules after import of package 'ai_content.cli', but prior to execution of 'ai_content.cli.main'; this may result in unpredictable behaviour
Music Providers:
  • lyria
  • minimax

Video Providers:
  • veo
  • kling

Image Providers:
  • imagen
```

### Presets

```
$ uv run -- python -m ai_content.cli.main list-presets
<frozen runpy>:128: RuntimeWarning: 'ai_content.cli.main' found in sys.modules after import of package 'ai_content.cli', but prior to execution of 'ai_content.cli.main'; this may result in unpredictable behaviour
Music Presets:
  • jazz: nostalgic (95 BPM)
  • blues: soulful (72 BPM)
  • ethiopian-jazz: mystical (85 BPM)
  • cinematic: epic (100 BPM)
  • electronic: euphoric (128 BPM)
  • ambient: peaceful (60 BPM)
  • lofi: relaxed (85 BPM)
  • rnb: sultry (90 BPM)
  • salsa: fiery (180 BPM)
  • bachata: romantic (130 BPM)
  • kizomba: sensual (95 BPM)

Video Presets:
  • nature: 16:9
  • urban: 21:9
  • space: 16:9
  • abstract: 1:1
  • ocean: 16:9
  • fantasy: 21:9
  • portrait: 9:16
```

## 1. Package Structure

### High-level structure (src/ai_content)

- Package entrypoint and exports: [src/ai_content/__init__.py](src/ai_content/__init__.py)
- CLI (Typer + Rich): [src/ai_content/cli/main.py](src/ai_content/cli/main.py)
- Core abstractions + registry: [src/ai_content/core/provider.py](src/ai_content/core/provider.py), [src/ai_content/core/registry.py](src/ai_content/core/registry.py), [src/ai_content/core/result.py](src/ai_content/core/result.py)
- Persistent job tracking (SQLite): [src/ai_content/core/job_tracker.py](src/ai_content/core/job_tracker.py)
- Config settings (Pydantic): [src/ai_content/config/settings.py](src/ai_content/config/settings.py)
- Providers (registered plugins): [src/ai_content/providers](src/ai_content/providers)
- Pipelines (orchestration): [src/ai_content/pipelines](src/ai_content/pipelines)
- Presets (music/video style catalogs): [src/ai_content/presets](src/ai_content/presets)
- Integrations (FFmpeg, YouTube): [src/ai_content/integrations](src/ai_content/integrations)
- Utilities (files, lyrics parsing, retry): [src/ai_content/utils](src/ai_content/utils)

### How providers are organized

- Each provider registers itself using decorator hooks in the registry, enabling plugin-style discovery. See [src/ai_content/core/registry.py](src/ai_content/core/registry.py).
- Importing [src/ai_content/providers/__init__.py](src/ai_content/providers/__init__.py) triggers provider module imports to register them.

### Purpose of pipelines

Pipelines sit above providers and coordinate multi-step workflows:
- Music-only workflows: [src/ai_content/pipelines/music.py](src/ai_content/pipelines/music.py)
- Video-only workflows: [src/ai_content/pipelines/video.py](src/ai_content/pipelines/video.py)
- Full music-video workflow: [src/ai_content/pipelines/full.py](src/ai_content/pipelines/full.py)

These pipelines connect presets, providers, and optional post-processing (like FFmpeg merging) into end-to-end flows.

### Text diagram of execution flow

```
CLI (Typer) 
  ↓
Pipelines (orchestrate multi-step: music → image → video → merge)
  ↓
Provider Registry → Provider implementation (Google/AIMLAPI/Kling)
  ↓
Async Jobs + SQLite Tracking → Exported file(s)
```

## 2. Provider Capabilities (from code)

### Music Providers

- **lyria**: Google Lyria RealTime streaming, instrumental only (no vocals). Uses a streaming session and writes WAV output. See [src/ai_content/providers/google/lyria.py](src/ai_content/providers/google/lyria.py).
- **minimax**: MiniMax via AIMLAPI. Supports lyrics and reference audio, polls async job status, downloads MP3 output. See [src/ai_content/providers/aimlapi/minimax.py](src/ai_content/providers/aimlapi/minimax.py).

**Vocals/lyrics support:** Only `minimax` has `supports_vocals = True` and accepts lyrics.

### Video Providers

- **veo**: Google Veo. Supports image-to-video via `first_frame_url`, polls operation status, outputs MP4. See [src/ai_content/providers/google/veo.py](src/ai_content/providers/google/veo.py).
- **kling**: KlingAI direct API. Supports image-to-video via `image_url`, JWT auth, long polling (5–14 min), outputs MP4. See [src/ai_content/providers/kling/direct.py](src/ai_content/providers/kling/direct.py).

**Image-to-video support:** Both `veo` and `kling` support image-to-video in provider code. The CLI accepts `--image`, but currently only warns about needing an image URL rather than uploading a local file. See [src/ai_content/cli/main.py](src/ai_content/cli/main.py).

### Image Providers

- **imagen**: Google Imagen (and optional Gemini image generation). See [src/ai_content/providers/google/imagen.py](src/ai_content/providers/google/imagen.py).

## 3. Preset System

Presets are defined as dataclasses in:
- Music presets: [src/ai_content/presets/music.py](src/ai_content/presets/music.py)
- Video presets: [src/ai_content/presets/video.py](src/ai_content/presets/video.py)

**Adding a new preset**: Add a new `MusicPreset` or `VideoPreset` entry to the corresponding registry dict (`MUSIC_PRESETS` or `VIDEO_PRESETS`) and it becomes discoverable via `list-presets`.

## 4. CLI Commands (from code)

From [src/ai_content/cli/main.py](src/ai_content/cli/main.py):

- `music` — Generate audio (supports `--style`, `--provider`, `--prompt`, `--bpm`, `--duration`, `--lyrics`, `--reference-url`, `--output`, `--force`).
- `video` — Generate video (supports `--style`, `--provider`, `--prompt`, `--aspect`, `--duration`, `--image`, `--output`).
- `list-providers` — Print available providers.
- `list-presets` — Print available presets.
- `music-status` — Poll MiniMax generation status and optionally download.
- `jobs` — List tracked jobs.
- `jobs-sync` — Sync pending jobs from API.
- `jobs-stats` — Show job statistics.

## 5. Job Tracking (SQLite)

The job tracker stores all generations in a local SQLite DB at `~/.ai-content/jobs.db` and includes duplicate detection using a hash of prompt + provider + content type + optional lyrics/reference URL. See [src/ai_content/core/job_tracker.py](src/ai_content/core/job_tracker.py).

## Key Insights / Notes

- Providers are pluggable via decorators, minimizing changes when adding new providers.
- Pipelines focus on orchestration and post-processing (including FFmpeg merge in [src/ai_content/integrations/media.py](src/ai_content/integrations/media.py)).
- Presets include culturally relevant options (e.g., `ethiopian-jazz`).
