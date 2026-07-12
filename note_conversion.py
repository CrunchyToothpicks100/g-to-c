# ruff: noqa: F841

import re

NOTE_RE = re.compile(r"^(?P<letter>[A-Ga-g])(?P<accidental>[#b]?)(?P<octave>-?\d+)?$")

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
