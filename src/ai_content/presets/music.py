"""
Music style presets.

Pre-configured prompt templates and settings for common music styles.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MusicPreset:
    """
    Music generation preset.

    Attributes:
        name: Preset identifier
        prompt: Style description prompt
        bpm: Recommended tempo
        mood: Emotional tone keyword
        tags: Additional style tags
    """

    name: str
    prompt: str
    bpm: int
    mood: str
    tags: list[str]


# === Music Style Presets ===

JAZZ = MusicPreset(
    name="jazz",
    prompt="""[Smooth Jazz Fusion]
[Walking Bass Line, Brushed Drums, Mellow Saxophone]
[Warm Piano Chords, Vinyl Crackle Texture]
Late night radio feel, nostalgic and contemplative""",
    bpm=95,
    mood="nostalgic",
    tags=["smooth", "fusion", "sophisticated"],
)

BLUES = MusicPreset(
    name="blues",
    prompt="""[Delta Blues]
[Bluesy Guitar Arpeggio, Smooth Bass Line]
[Vintage Amplifier Warmth, Slight Distortion]
Raw emotional delivery, soulful and authentic""",
    bpm=72,
    mood="soulful",
    tags=["delta", "raw", "authentic"],
)

ETHIOPIAN_JAZZ = MusicPreset(
    name="ethiopian-jazz",
    prompt="""[Ethiopian Jazz Fusion with Ethio-Jazz Influence]
[Masenqo-inspired Strings, Kirar melodic patterns]
[Syncopated African rhythms, Modal scales]
[Brass section, Sophisticated jazz harmonies]
Mulatu Astatke inspired, 1970s Addis Ababa sound""",
    bpm=85,
    mood="mystical",
    tags=["ethio-jazz", "modal", "african"],
)

CINEMATIC = MusicPreset(
    name="cinematic",
    prompt="""[Epic Orchestral]
[Sweeping Strings, Powerful Brass Section]
[Timpani Build, Choir Crescendo]
[Film Score Quality, Emotional Arc]
Hans Zimmer inspired, triumphant and emotional""",
    bpm=100,
    mood="epic",
    tags=["orchestral", "film-score", "triumphant"],
)

ELECTRONIC = MusicPreset(
    name="electronic",
    prompt="""[Progressive House]
[Driving Bass, Synth Arpeggios]
[Build-up with Risers, Drop with Heavy Kick]
[Atmospheric Pads, Glitchy Textures]
Festival anthem energy, euphoric drops""",
    bpm=128,
    mood="euphoric",
    tags=["house", "edm", "festival"],
)

AMBIENT = MusicPreset(
    name="ambient",
    prompt="""[Ambient Soundscape]
[Ethereal Pads, Gentle Textures]
[Reverb-drenched Piano, Subtle Modular Synth]
[Field Recordings, Nature Sounds]
Brian Eno inspired, meditative and peaceful""",
    bpm=60,
    mood="peaceful",
    tags=["ambient", "meditative", "eno"],
)

LOFI = MusicPreset(
    name="lofi",
    prompt="""[Lo-fi Hip-Hop]
[Vinyl Crackle, Dusty Drum Loops]
[Mellow Jazz Samples, Sidechain Compression]
[Warm Tape Saturation, Calm Vibes]
Study beats, relaxing and nostalgic""",
    bpm=85,
    mood="relaxed",
    tags=["lofi", "chill", "study"],
)

RNB = MusicPreset(
    name="rnb",
    prompt="""[Contemporary R&B]
[Smooth Synth Pads, 808 Bass]
[Trap-influenced Hi-Hats, Neo-Soul Chords]
[Sultry Vocal Space, Late Night Feel]
Modern R&B production, emotional and smooth""",
    bpm=90,
    mood="sultry",
    tags=["rnb", "neo-soul", "modern"],
)

SALSA = MusicPreset(
    name="salsa",
    prompt="""[Cuban Salsa Dura]
[Driving Tumbao Piano, Syncopated Clave Pattern]
[Blazing Trumpet Section, Trombone Harmonies]
[Congas, Bongos, Timbales Percussion]
[Montuno Piano Riffs, Call and Response]
Fania Records inspired, fiery and danceable""",
    bpm=180,
    mood="fiery",
    tags=["salsa", "latin", "cuban"],
)

BACHATA = MusicPreset(
    name="bachata",
    prompt="""[Dominican Bachata Romántica]
[Requinto Guitar Melodic Lead, Güira Rhythm]
[Bongo Patterns, Syncopated Bass Line]
[Romantic Guitar Arpeggios, Emotional Delivery]
[Modern Bachata Sensual Elements]
Romeo Santos inspired, passionate and romantic""",
    bpm=130,
    mood="romantic",
    tags=["bachata", "latin", "dominican"],
)

KIZOMBA = MusicPreset(
    name="kizomba",
    prompt="""[Angolan Kizomba]
[Deep Electronic Bass, Slow Sensual Groove]
[Zouk-influenced Synths, African Percussion]
[Romantic Melodies, Intimate Atmosphere]
[Warm Pad Textures, Subtle Beat Patterns]
Lusophone African sound, sensual and hypnotic""",
    bpm=95,
    mood="sensual",
    tags=["kizomba", "zouk", "african"],
)


# Registry of all presets
MUSIC_PRESETS: dict[str, MusicPreset] = {
    preset.name: preset
    for preset in [
        JAZZ,
        BLUES,
        ETHIOPIAN_JAZZ,
        CINEMATIC,
        ELECTRONIC,
        AMBIENT,
        LOFI,
        RNB,
        SALSA,
        BACHATA,
        KIZOMBA,
    ]
}


def get_preset(name: str) -> MusicPreset:
    """
    Get a music preset by name.

    Args:
        name: Preset name (e.g., "jazz", "cinematic")

    Returns:
        MusicPreset instance

    Raises:
        KeyError: If preset not found
    """
    if name not in MUSIC_PRESETS:
        available = list(MUSIC_PRESETS.keys())
        raise KeyError(f"Music preset '{name}' not found. Available: {available}")
    return MUSIC_PRESETS[name]


def list_presets() -> list[str]:
    """List all available preset names."""
    return list(MUSIC_PRESETS.keys())
