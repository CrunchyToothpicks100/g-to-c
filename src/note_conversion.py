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
    "♯": 1,
    "♭": -1,
}

SEMITONE_TO_NOTE = {
    0: "C",
    1: "C♯",
    2: "D",
    3: "D♯",
    4: "E",
    5: "F",
    6: "F♯",
    7: "G",
    8: "G♯",
    9: "A",
    10: "A♯",
    11: "B",
}

SEMITONE_TO_NOTE_FLATS = {
    0: "C",
    1: "D♭",
    2: "D",
    3: "E♭",
    4: "E",
    5: "F",
    6: "G♭",
    7: "G",
    8: "A♭",
    9: "A",
    10: "B♭",
    11: "B",
}

SEMITONE_TO_IVLS = {
    0: "root",
    1: "♭2",
    2: "2nd",
    3: "♭3",
    4: "3rd",
    5: "4th",
    6: "♭5",
    7: "5th",
    8: "♭6",
    9: "6th",
    10: "♭7",
    11: "maj7",
}

# Regex hell
NOTE_RE = re.compile(r"^(?P<letter>[A-Ga-g])(?P<accidental>[#b♯♭]?)(?P<octave>-?\d+)?$")


def _parse_note(word: str) -> tuple[str, str, str | None]:
    match = NOTE_RE.fullmatch(word.strip())
    if not match:
        raise ValueError(f"Invalid note: {word!r}")

    return (
        match.group("letter"),
        match.group("accidental"),
        match.group("octave"),
    )


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

    octave, semitone = divmod(num, 12)  # Quotient, Remainder
    note_map = SEMITONE_TO_NOTE_FLATS if accidental == "flat" else SEMITONE_TO_NOTE
    note = note_map[semitone]
    return f"{note}{octave}"


# F#2 -> Gb2, Db3 -> C#3
def switch_accidental(word: str) -> str:
    letter, accidental, octave = _parse_note(word)

    if accidental in ["#", "♯"]:
        letter = chr(ord(letter) + 1)
        accidental = "♭"
    elif accidental in ["b", "♭"]:
        letter = chr(ord(letter) - 1)
        accidental = "♯"

    if octave is None:
        octave = ""

    return letter + accidental + octave


# Helper functions


# C2 -> C
def _strip_octave(note: str) -> str:
    return re.sub(r"\d+$", "", note)


def _get_stable_root_index(intervals: list[int]) -> int:
    if len(intervals) in (1, 2):
        return 0

    stable_root_index = 0
    target = 0
    for i in range(len(intervals)):
        fifths_or_octaves = 0
        for j in range(len(intervals)):
            ivl = (intervals[j] - intervals[i]) % 12
            if ivl in (7, 12):
                fifths_or_octaves += 1
        if fifths_or_octaves > target:
            target = fifths_or_octaves
            stable_root_index = i

    return stable_root_index


def _no_sus_or_3rd(ivls: set[int]) -> bool:
    return {2, 3, 4, 5}.isdisjoint(ivls)


def _has_sus_or_3rd(ivls: set[int]) -> bool:
    return not {2, 3, 4, 5}.isdisjoint(ivls)


def _no_7th_or_6th(ivls: set[int]) -> bool:
    return {9, 10, 11}.isdisjoint(ivls)


def _no_7th(ivls: set[int]) -> bool:
    return {10, 11}.isdisjoint(ivls)


def _notate_ivls(ivls: set[int]) -> list[str]:
    return [SEMITONE_TO_IVLS[i % 12] for i in ivls]


# Example (standard tuning):
# fret_notes(('x', 0, 3, 2, 1, 1))
# -> A, F, A, C, F
# -> 10, 18, 22, 25, 30
# root_idx = 1
# offset = 18
# stable_ivls = [-8, 0, 4, 7, 0]
# chord = "F/A"
#
# Note: find_slash=True will not work if find_inversion=False
#
def notes_to_chord(
    notes: list[str],
    *,
    verbose: bool = True,
    find_inversion: bool = False,
    find_slash: bool = True,
    find_poly: bool = True,
) -> str:
    if len(notes) == 0:
        raise ValueError("'notes' cannot be empty.")
    if len(notes) == 1:
        raise ValueError(f"'notes' only has one note: {notes[0]}")
    if len(notes) == 2:
        dyad = _strip_octave(notes[0]) + "+" + _strip_octave(notes[1]) + " dyad"
        return dyad

    intervals = [note_to_num(note) for note in notes]
    root_idx = _get_stable_root_index(intervals) if find_inversion else 0
    offset = intervals[root_idx]
    offset_ivls = [x - offset for x in intervals]

    # Find root note, strip the octave number
    root_note: str = _strip_octave(notes[root_idx])

    # Escape power chords
    is_power = set([x % 12 for x in offset_ivls]).issubset(
        {0, 7}
    )  # ONLY octaves and perf 5s
    if is_power:
        chord = root_note + "5"
        return chord

    # Sets used for dropping duplicates and O(1) search
    stable_ivls: set[int] = set()
    extension_ivls: set[int] = set()

    poly_chords: list[tuple[str, str]] = []
    if find_poly:
        if len(offset_ivls) < 4:
            print("INFO: Poly chords must have at least 4 notes")
        else:
            for i in range(2, len(offset_ivls) - 1):
                poly_chords.append(
                    (
                        notes_to_chord(
                            notes[0:i],
                            verbose=False,
                            find_inversion=True,
                            find_slash=False,
                            find_poly=False,
                        ),
                        notes_to_chord(
                            notes[i:],
                            verbose=False,
                            find_inversion=True,
                            find_slash=False,
                            find_poly=False,
                        ),
                    )
                )

    slash_chord = ""
    if find_slash:
        if len(offset_ivls) < 3:
            print("INFO: Slash chords must have at least 3 notes")
        else:
            slash_chord = (
                notes_to_chord(
                    notes[1:],
                    verbose=False,
                    find_slash=False,
                    find_poly=False,
                    find_inversion=find_inversion,
                )
                + "/"
                + _strip_octave(notes[0])
            )

    # Separate interval lists by octave
    # Unison notes not needed
    # All perf 5ths are stable
    for ivl in offset_ivls:
        mod_ivl = ivl % 12
        if mod_ivl != 0:
            if ivl < 13 or mod_ivl == 7:
                stable_ivls.add(mod_ivl)
            else:
                extension_ivls.add(mod_ivl)

    # if no sus or 3rd, try pulling ONE interval from higher octaves
    # Search order: major, minor, sus4, sus2
    if _no_sus_or_3rd(stable_ivls):
        for i in (4, 3, 5, 2):
            if i in extension_ivls:
                stable_ivls.add(i)
                extension_ivls.remove(i)
                break

    # if sus or 3rd exists with no 7 or 6, pull ONE 7 or 6 from extension list
    if _has_sus_or_3rd(stable_ivls) and _no_7th_or_6th(stable_ivls):
        for i in (10, 11, 9):
            if i in extension_ivls:
                stable_ivls.add(i)
                extension_ivls.remove(i)
                break

    # if no sus or 3rd at all, push ALL 7s to extension list
    if _no_sus_or_3rd(stable_ivls):
        for i in [10, 11]:
            if i in stable_ivls:
                extension_ivls.add(i)
                stable_ivls.remove(i)

    # Only ONE of these four booleans will be true
    is_major = 4 in stable_ivls
    is_minor = 3 in stable_ivls and not is_major
    is_sus4 = 5 in stable_ivls and not (is_major or is_minor)
    is_sus2 = 2 in stable_ivls and not (is_sus4 or is_major or is_minor)

    no_perf_5 = 7 not in stable_ivls

    is_dim = {3, 6}.issubset(stable_ivls) and no_perf_5
    is_aug = {4, 8}.issubset(stable_ivls) and no_perf_5

    # Try to build augmented triad with higher octaves
    if is_major and not is_aug and 8 in extension_ivls:
        stable_ivls.add(8)
        extension_ivls.remove(8)
        is_aug = True

    # Try to build diminished triad with higher octaves
    elif is_minor and not is_dim and 6 in extension_ivls:
        stable_ivls.add(6)
        extension_ivls.remove(6)
        is_dim = True

    # While techinically augmented or diminished,
    # These chords have special notation: Cm7(b5), C7(#5), Cmaj7(#5)
    notate_dim = is_dim and _no_7th(stable_ivls)
    notate_aug = is_aug and _no_7th(stable_ivls)

    # Notate the triad, sus chords are separate for notation
    sus = "sus4" if is_sus4 else "sus2" if is_sus2 else ""
    triad = ""
    if notate_aug:
        triad = "aug"
    elif notate_dim:
        triad = "dim"
    elif is_minor:
        triad = "m"

    is_dim7 = is_dim and 9 in stable_ivls  # diminished with bb7 (6th)
    is_dom7 = 10 in stable_ivls and not is_dim7
    is_maj7 = 11 in stable_ivls and not is_dom7
    is_seven = is_dim7 or is_dom7 or is_maj7
    is_six = 9 in stable_ivls and not (is_seven or is_dim)

    six = "6" if is_six else ""

    # Sets are used to prevent duplicates
    parenthetical: set[str] = set()
    additions: set[str] = set()

    if not any([is_major, is_minor, is_sus2, is_sus4]):
        parenthetical.add("no3")

    # 0: -- pass on root
    # 1: minor 2nd              # ext: b9
    # 2: 2nd                    # ext: 9
    # 3: minor 3rd              # ext: #9
    # 4: -- pass on maj 3rd
    # 5: perf 4th               # ext: 11
    # 6: b5 or #4
    # 7: -- pass on perf 5th
    # 8: #5, b6                 # ext: b13
    # 9: 6th                    # ext: 13
    # 10: -- pass on dom 7th
    # 11: maj 7th
    for ivl in stable_ivls:
        match ivl:
            case 1:  # m2
                additions.add("♭2")
            case 2:  # 2
                if not is_sus2:
                    additions.add("2")
            case 3:  # m3
                if is_major:
                    additions.add("♭3")
            case 5:  # perf 4
                if not is_sus4:
                    additions.add("4")
            case 6:  # b5
                if not is_dim:
                    if is_major:
                        additions.add("♯4")
                    else:
                        additions.add("♭5")
                elif is_dim and not notate_dim:
                    parenthetical.add("♭5")
            case 8:  # b6
                if not is_aug:
                    if is_minor:
                        parenthetical.add("♭6")
                    else:
                        additions.add("♭6")
                elif is_aug and not notate_aug:
                    parenthetical.add("♯5")
            case 11:  # maj7
                if not is_maj7:
                    additions.add("maj7")  # EXTREME dissonance!
                # Note: remember that dom7s are pulled first
                # and dom7s are True before maj7s

    highest_seven = 7

    for ivl in extension_ivls:
        match ivl:
            case 1:  # m2
                if is_seven:
                    parenthetical.add("♭9")
                else:
                    additions.add("♭9")
            case 2:  # 2
                if is_seven:
                    highest_seven = max(9, highest_seven)
                elif is_six:
                    six = "6/9"
                else:
                    additions.add("9")
            case 3:  # m3
                if is_seven:
                    parenthetical.add("♯9")
                elif is_major:
                    additions.add("♯9")
            case 5:  # perf 4
                if is_seven:
                    highest_seven = max(11, highest_seven)
                else:
                    parenthetical.add("add11")
            case 6:  # b5
                if is_dom7 or is_maj7:
                    parenthetical.add("♯11")
                elif not is_dim:
                    additions.add("♯11")
            case 8:  # b6
                if is_dom7 or is_dim7:
                    parenthetical.add("♭13")
                else:
                    additions.add("♭13")
            case 9:  # 6
                if is_seven:
                    highest_seven = max(13, highest_seven)
                elif not is_six:
                    additions.add("13")
            case 11:  # maj7
                if not is_maj7:
                    parenthetical.add("add maj7")  # EXTREME dissonance

    seventh = ""
    if is_seven:
        if is_maj7:
            seventh = "maj"
        seventh += str(highest_seven)

    chord = root_note + triad + six + seventh + sus

    if parenthetical:  # pythonic version of "not empty"
        chord += "(" + ",".join(parenthetical) + ")"

    if additions:
        chord += f"add{','.join(list(additions))}"

    if verbose:
        print(f"Intervals: {intervals}")
        print(f"Root Index: {root_idx}")
        print(f"Semitone offset: {offset}")
        print(f"Offset intervals: {_notate_ivls(set(offset_ivls))}")
        print(f"Stable intervals: {_notate_ivls(stable_ivls)}")
        print(f"Extension intervals: {_notate_ivls(extension_ivls)}")
        print()
        print(f"is_aug: {is_aug}")
        print(f"notate_aug: {notate_aug}")
        print()
        print(f"Parenthetical: {parenthetical if parenthetical else 'none'}")
        print(f"Additions: {additions if additions else 'none'}")
        print()
        print(f"Root note: {root_note}")
        print(f"Triad: {triad if triad else 'none'}")
        print(f"Sus: {sus if sus else 'none'}")
        print(f"Highest seven: {seventh if seventh else 'none'}")
        print()
        if find_slash and slash_chord:
            print(f"Slash chord: {slash_chord if slash_chord else 'none'}")
            print()
        if find_poly and poly_chords:
            print("Poly chords: ")
            for ch in poly_chords:
                print(f"\tBass: {ch[0]}")
                print(f"\ttreble: {ch[1]}")
                print()
        print(f"Chord: {chord}")

    return chord
