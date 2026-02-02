"""
Lyrics parser with structure tag injection.

Adds [Verse], [Chorus], [Bridge] tags to raw lyrics
following AI music generation best practices.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class StructuredLyrics:
    """Parsed lyrics with structure."""

    raw: str
    structured: str
    style_header: str
    verse_count: int
    chorus_count: int
    has_bridge: bool


# Style headers for different genres
STYLE_HEADERS = {
    "jazz": "[Smooth Jazz, Sophisticated Vocals, Scat Improvisation]",
    "blues": "[Delta Blues, Raw Emotional Delivery, Gritty Voice]",
    "pop": "[Modern Pop, Clear Crisp Vocals, Radio Ready]",
    "rock": "[Alternative Rock, Powerful Voice, Guitar Drive]",
    "soul": "[Neo Soul, Smooth R&B Vocal, Warm Harmonies]",
    "rnb": "[Contemporary R&B, Silky Vocals, Groove]",
    "hiphop": "[Hip-Hop, Confident Flow, Rhythmic Delivery]",
    "country": "[Country, Storytelling Vocal, Acoustic Guitar]",
    "electronic": "[Electronic Pop, Vocoder Effects, Dance Energy]",
    "folk": "[Folk, Intimate Vocal, Acoustic Warmth]",
}


def parse_lyrics_with_structure(
    raw_lyrics: str,
    style: str = "pop",
    auto_detect_structure: bool = True,
) -> StructuredLyrics:
    """
    Parse raw lyrics and add structure tags.

    Args:
        raw_lyrics: Plain text lyrics
        style: Music style for header tag
        auto_detect_structure: Whether to auto-detect verses/choruses

    Returns:
        StructuredLyrics with tagged content

    Example:
        >>> lyrics = parse_lyrics_with_structure('''
        ... Walking through the city lights
        ... Finding my way home tonight
        ...
        ... This is where I belong
        ... This is my song
        ... ''', style="pop")
        >>> print(lyrics.structured)
    """
    lines = raw_lyrics.strip().split("\n")
    structured = []

    # Add style header
    style_header = STYLE_HEADERS.get(style.lower(), STYLE_HEADERS["pop"])
    structured.append(style_header)
    structured.append("")

    verse_count = 0
    chorus_count = 0
    has_bridge = False

    # Track seen lines for chorus detection
    seen_lines: set[str] = set()
    line_groups: list[list[str]] = []
    current_group: list[str] = []

    # First pass: group lines by blank line separators
    for line in lines:
        line = line.strip()
        if not line:
            if current_group:
                line_groups.append(current_group)
                current_group = []
        else:
            current_group.append(line)

    if current_group:
        line_groups.append(current_group)

    # Second pass: classify groups and add structure tags
    for group in line_groups:
        if not group:
            continue

        # Check if group already has structure tags
        first_line = group[0]
        if first_line.startswith("[") and first_line.endswith("]"):
            # Already has a tag, keep as-is
            structured.extend(group)
            structured.append("")

            # Count for stats
            tag_lower = first_line.lower()
            if "verse" in tag_lower:
                verse_count += 1
            elif "chorus" in tag_lower:
                chorus_count += 1
            elif "bridge" in tag_lower:
                has_bridge = True
            continue

        if auto_detect_structure:
            # Check if this group matches any previous lines (likely chorus)
            group_text = " ".join(group).lower()
            is_repeat = any(
                line.lower() in group_text
                for line in seen_lines
                if len(line) > 10  # Only check substantial lines
            )

            if is_repeat and chorus_count == 0:
                # First repeat is likely chorus
                chorus_count += 1
                structured.append(f"[Chorus]")
            elif is_repeat:
                chorus_count += 1
                structured.append(f"[Chorus {chorus_count}]")
            else:
                verse_count += 1
                if verse_count == 1:
                    structured.append("[Verse 1]")
                else:
                    structured.append(f"[Verse {verse_count}]")

            # Add lines to seen set
            for line in group:
                if len(line) > 5:
                    seen_lines.add(line)
        else:
            # No auto-detection, just add verse tags
            verse_count += 1
            structured.append(f"[Verse {verse_count}]")

        structured.extend(group)
        structured.append("")

    # Add outro hint if needed
    if len(line_groups) > 4 and not has_bridge:
        # Could add bridge detection here
        pass

    return StructuredLyrics(
        raw=raw_lyrics,
        structured="\n".join(structured),
        style_header=style_header,
        verse_count=verse_count,
        chorus_count=chorus_count,
        has_bridge=has_bridge,
    )


def add_vocal_directions(
    lyrics: str,
    directions: dict[str, str] | None = None,
) -> str:
    """
    Add vocal directions to lyrics.

    Args:
        lyrics: Structured lyrics text
        directions: Mapping of section -> direction

    Example:
        >>> add_vocal_directions(lyrics, {
        ...     "Verse 1": "(soft, intimate)",
        ...     "Chorus": "(powerful, belt)",
        ... })
    """
    if directions is None:
        return lyrics

    result = lyrics
    for section, direction in directions.items():
        # Find section tag and add direction after it
        pattern = rf"(\[{re.escape(section)}\])"
        replacement = rf"\1\n{direction}"
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def extract_lyrics_sections(lyrics: str) -> dict[str, list[str]]:
    """
    Extract sections from structured lyrics.

    Returns:
        Dict mapping section names to line lists
    """
    sections: dict[str, list[str]] = {}
    current_section = "intro"
    current_lines: list[str] = []

    for line in lyrics.split("\n"):
        line = line.strip()

        # Check for section tag
        if line.startswith("[") and line.endswith("]"):
            # Save previous section
            if current_lines:
                sections[current_section] = current_lines

            # Start new section
            current_section = line[1:-1]  # Remove brackets
            current_lines = []
        elif line:
            current_lines.append(line)

    # Save last section
    if current_lines:
        sections[current_section] = current_lines

    return sections
