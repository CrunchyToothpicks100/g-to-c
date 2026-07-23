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


# C2 -> C
def strip_octave(note: str) -> str:
    return re.sub(r"\d+$", "", note)


# example: fret_notes(('x', 0, 3, 2, 1, 1), g_capo_1)
# -> A#, F#, A#, C#, F#
# -> 10, 18, 22, 25, 30
# root_idx = 1
# offset = 18
# stable_ivls = [-8, 0, 4, 7, 0]
# chord = "F#/A#"
def notes_to_chord(notes: list[str], quiet: bool = False) -> str:
    if len(notes) == 0:
        raise ValueError("'notes' cannot be empty.")

    intervals = [note_to_num(note) for note in notes]
    root_idx = get_stable_root_index(intervals)
    offset = intervals[root_idx]
    stable_ivls = tuple((x - offset) % 12 for x in intervals)

    if not quiet:
        print(
            f"Intervals: {intervals}\n",
            f"Root Index: {root_idx}\n",
            f"Offset: {offset}\n",
            f"Stable intervals: {stable_ivls}\n",
        )

    is_major = 4 in stable_ivls
    is_minor = 3 in stable_ivls and not is_major
    is_sus4 = 5 in stable_ivls and not (is_major or is_minor)
    is_sus2 = 2 in stable_ivls and not (is_sus4 or is_major or is_minor)
    is_power = set(stable_ivls).issubset({0, 7})  # ONLY octaves and perf 5s
    is_dim = {3, 6}.issubset(stable_ivls) and {7, 10, 11}.isdisjoint(
        stable_ivls
    )  # must have triad, no perf 5s or 7s
    is_aug = {4, 8}.issubset(stable_ivls) and {7, 10, 11}.isdisjoint(
        stable_ivls
    )  # must have triad, no perf 5s or 7s
    is_dim7 = is_dim and 9 in stable_ivls  # must be diminished with bb7 (b6)
    is_dom7 = 10 in stable_ivls
    is_maj7 = 11 in stable_ivls
    has_seven = is_dim7 or is_dom7 or is_maj7  # These chords will use 13 rather than 6
    has_six = not {8, 9}.isdisjoint(stable_ivls) and not has_seven  # Includes aug

    if not quiet:
        print(
            f"is_major: {is_major}\n"
            + f"is_minor: {is_minor}\n"
            + f"is_sus4: {is_sus4}\n"
            + f"is_sus2: {is_sus2}\n"
            + f"is_power: {is_power}\n"
            + f"is_dim: {is_dim}\n"
            + f"is_aug: {is_aug}\n"
            + f"is_dim7: {is_dim7}\n"
            + f"is_dom7: {is_dom7}\n"
            + f"is_maj7: {is_maj7}\n"
            + f"has_seven: {has_seven}\n"
            + f"has_six: {has_six}\n"
        )

    # Find root note, strip the octave number
    root_note = strip_octave(notes[root_idx])
    triad = (
        "dim"
        if is_dim
        else "aug"
        if is_aug
        else ""
        if is_major
        else "m"
        if is_minor
        else "5"
        if is_power
        else ""
    )
    sus = "sus" if is_sus4 else "sus2" if is_sus2 else ""
    six: list[str] = []
    seven = "7" if is_dom7 or is_dim7 else "maj7" if is_maj7 else ""
    extensions: list[str] = []
    slash = ""

    if root_idx > 1:
        slash = "/" + notes_to_chord(notes[0:root_idx], quiet=True)
    elif root_idx == 1:
        slash = "/" + notes[0]

    if not quiet:
        print("Case matches:", end="")
    # 1: b9
    # 2: sus2
    # 3: minor (#9)
    # 4: (major)
    # 5: sus4
    # 6: b5 (dim?)
    # 7: 5
    # 8: #5, b6 (aug?)
    # 9: 6
    # 10: b7
    # 11: maj7
    for ivl in stable_ivls:
        match ivl:
            case 1:  # m2
                extensions.append("b9" if has_seven else "addb9")
                if not quiet:
                    print("m2, ", end="")
            case 2:  # 2
                if is_major or is_minor or is_sus4:
                    if is_dom7 or is_dim7:
                        seven = "9"
                    elif is_maj7:
                        seven = "maj9"
                    elif has_six:
                        six.append("9")
                    else:
                        extensions.append("add9")
                if not quiet:
                    print("2, ", end="")
            case 3:  # m3
                if is_major:
                    extensions.append("#9" if has_seven else "add#9")
                if not quiet:
                    print("m3, ", end="")
                    # 3 (pass)
            case 5:  # 4
                if is_major or is_minor:
                    if is_dom7 or is_dim7:
                        seven = "11"
                    elif is_maj7:
                        seven = "maj11"
                    elif has_six:
                        six.append("11")
                    else:
                        extensions.append("add11")
                if not quiet:
                    print("4, ", end="")
            case 6:  # b5
                if is_major:
                    extensions.append("#11" if has_seven else "add#11")
                elif not is_dim:
                    extensions.append("b5")
                if not quiet:
                    print("b5, ", end="")
                    # 5 (pass)
            case 8:  # b6
                if is_dom7:
                    extensions.append("b13")
                elif is_maj7:
                    extensions.append("#5")
                elif not has_six:
                    extensions.append("b6")
                if not quiet:
                    print("b6, ", end="")
            case 9:  # 6
                if is_major or is_minor:
                    if is_dom7 or is_dim7:
                        seven = "13"
                    elif is_maj7:
                        seven = "maj13"
                    elif has_six:
                        six.append("13")
                if not quiet:
                    print("6, ", end="")

    if not quiet:
        print("\n")  # Blank line after case matches

    if not (is_major or is_minor or is_power):
        extensions.append("no3")

    chord = root_note + triad + "/".join(six) + seven + sus

    if extensions:  # pythonic version of "not empty"
        chord += "(" + ",".join(extensions) + ")"
    if slash:
        chord += strip_octave(slash)

    if not quiet:
        print(
            f"Root note: {root_note}\n"
            + f"Triad: {triad}\n"
            + f"Sus: {sus}\n"
            + f"Six list: {six}\n"
            + f"Highest seven: {seven}\n"
            + f"Extensions list: {extensions}\n"
            + f"Slash: {slash}\n"
        )

    print(f"Chord: {chord}")

    return chord


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
