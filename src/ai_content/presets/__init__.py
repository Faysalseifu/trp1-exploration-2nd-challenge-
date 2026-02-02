"""Presets module exports."""

from ai_content.presets.music import (
    MusicPreset,
    MUSIC_PRESETS,
    get_preset as get_music_preset,
    list_presets as list_music_presets,
    # Named presets
    JAZZ,
    BLUES,
    ETHIOPIAN_JAZZ,
    CINEMATIC,
    ELECTRONIC,
    AMBIENT,
    LOFI,
    RNB,
)
from ai_content.presets.video import (
    VideoPreset,
    VIDEO_PRESETS,
    get_preset as get_video_preset,
    list_presets as list_video_presets,
    # Named presets
    NATURE,
    URBAN,
    SPACE,
    ABSTRACT,
    OCEAN,
    FANTASY,
    PORTRAIT,
)

__all__ = [
    # Music
    "MusicPreset",
    "MUSIC_PRESETS",
    "get_music_preset",
    "list_music_presets",
    "JAZZ",
    "BLUES",
    "ETHIOPIAN_JAZZ",
    "CINEMATIC",
    "ELECTRONIC",
    "AMBIENT",
    "LOFI",
    "RNB",
    # Video
    "VideoPreset",
    "VIDEO_PRESETS",
    "get_video_preset",
    "list_video_presets",
    "NATURE",
    "URBAN",
    "SPACE",
    "ABSTRACT",
    "OCEAN",
    "FANTASY",
    "PORTRAIT",
]
