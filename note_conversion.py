# ruff: noqa: F841

import re

NOTE_TO_SEMITONE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

ACCIDENTAL_TO_OFFSET = {
    "": 0,
    "#": 1,
    "b": -1,
}

SEMITONE_TO_NOTE = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}

SEMITONE_TO_NOTE_FLATS = {
    0: "C",
    1: "Db",
    2: "D",
    3: "Eb",
    4: "E",
    5: "F",
    6: "Gb",
    7: "G",
    8: "Ab",
    9: "A",
    10: "Bb",
    11: "B",
}

INTERVAL_TO_NAME = {
    0: "unison",
    1: "b2",
    2: "sus2",
    3: "minor",
    4: "major",
    5: "sus4",
    6: "b5",
    7: "5",
    8: "aug",
    9: "6",
    10: "b7",
    11: "maj7",
    12: "octave",
    13: "b9",
    14: "add9",
    17: "add13",
    18: "#13"
}

# Regex hell
NOTE_RE = re.compile(r"^(?P<letter>[A-Ga-g])(?P<accidental>[#b]?)(?P<octave>-?\d+)?$")

def _parse_note(word: str) -> tuple[str, str, str | None]:
    match = NOTE_RE.fullmatch(word.strip())
    if not match:
        raise ValueError(f"Invalid note: {word!r}")

    return match.group("letter"), match.group("accidental"), match.group("octave")


# C0 = 0, C#0 = 1, etc.
def note_to_num(word: str) -> int:
    letter, accidental, octave = _parse_note(word)
    semitone = NOTE_TO_SEMITONE[letter.upper()]
    semitone += ACCIDENTAL_TO_OFFSET[accidental]

    octave_num = int(octave) if octave is not None else 0
    return octave_num * 12 + semitone


# 10 = "A#0", 20 = "G#1"
def num_to_note(
        num: int,
        accidental: str = "sharp",
) -> str:
    if accidental not in {"sharp", "flat"}:
        raise ValueError("accidental must be 'sharp' or 'flat'")

    octave, semitone = divmod(num, 12)
    note_map = SEMITONE_TO_NOTE_FLATS if accidental == "flat" else SEMITONE_TO_NOTE
    note = note_map[semitone]
    return f"{note}{octave}"


# F#2 -> Gb2, Db3 -> C#3
def switch_accidental(word: str) -> str:
    letter, accidental, octave = _parse_note(word)

    if accidental == "#":
        letter = chr(ord(letter) + 1)
        accidental = "b"
    elif accidental == "b":
        letter = chr(ord(letter) - 1)
        accidental = "#"

    if octave is None:
        octave = ""

    return letter + accidental + octave


# Intervals are measured in semitones, or half-steps
def notes_to_chord(
        notes: list[str],
        quiet: bool = False
) -> str:
    if len(notes) == 0:
        raise ValueError("'notes' cannot be empty.")

    intervals = [note_to_num(note) for note in notes]       # example: Bb, Gb, Db -> 10, 18, 25
    root_idx = get_stable_root_index(intervals)             # root_idx = 1
    offset = intervals[root_idx]                            # offset = 18
    stable_intervals = [x - offset for x in intervals]      # -8, 0, 7

    chord = ""

    if root_idx > 1:
        chord += "/" + notes_to_chord(notes[0:root_idx])
    elif root_idx == 1:
        chord += "/" + notes[0]

    return str(stable_intervals)


def interval_to_name(interval: int) -> str:
    while interval > 0:
        name = INTERVAL_TO_NAME.get(interval)
        if name is not None:
            return name
        interval -= 12
    return ""

def get_stable_root_index(intervals: list[int]) -> int:
    if len(intervals) in [1, 2]:
        return 0

    stable_root_index = 0
    target = 0
    i = 0
    j = 0
    for i in range(len(intervals)):
        fifths_or_octaves = 0
        for j in range(len(intervals)):
            ivl = (intervals[j] - intervals[i]) % 12
            if ivl in [7, 12]:
                fifths_or_octaves += 1
        if fifths_or_octaves > target:
            target = fifths_or_octaves
            stable_root_index = i

    return stable_root_index


