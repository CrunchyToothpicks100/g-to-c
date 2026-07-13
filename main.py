from __future__ import annotations
from dataclasses import dataclass

import note_conversion as nc
import guitar_registry as gr

# See GUITAR_TUNING.md for tuning info

@dataclass
class Guitar:
    name: str
    tuning: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.tuning, tuple):
            self.tuning = tuple(self.tuning)

        if not self.tuning:
            raise ValueError("Tuning must contain at least one string")

    # For printing tuning
    # High to low is default unless high_to_low=False is specified
    def get_tuning(self, high_to_low: bool = True) -> None:
        if high_to_low:
            string_numbers = range(1, len(self.tuning) + 1)  # 1, 2, 3, ...
            strings_zip = zip(string_numbers, tuple(reversed(self.tuning)))
        else:
            string_numbers = range(len(self.tuning), 0, -1)  # ..., 3, 2, 1
            strings_zip = zip(string_numbers, self.tuning)

        output: list[str] = []

        for string_number, note in strings_zip:
            which_side = ""
            if string_number == len(self.tuning):
                which_side = "(low)"
            if string_number == 1:
                which_side = "(high)"
            output.append(f"String {string_number}: {note} {which_side}".rstrip())

        print("\n".join(output))

    # guitar_string is the actual string number, not the index
    def fret(self, guitar_string: int, fret_num: int, accidental: str = "sharp") -> str:
        strings = self.tuning

        if guitar_string < 1 or guitar_string > len(strings):
            raise IndexError("guitar_string is out of range for this tuning")

        open_string = strings[len(strings) - guitar_string]
        open_note_num = nc.note_to_num(open_string)
        semitone = open_note_num + fret_num
        return nc.num_to_note(semitone, accidental)

    # -1 or 'x' means "muted string"
    # Example: A# power chord on bass
    # ba = load_guitar("bass", tuning=("E1", "A1", "D2", "G2"))
    # ba.fret_notes(('x', 1, 3, 'x'))
    def fret_notes(
            self,
            fret_nums: tuple[str|int, ...],
            accidental: str = "sharp",
            quiet: bool = False
    ) -> str:
        notes = []
        i = len(self.tuning)
        for fret_num in fret_nums:
            if fret_num == 'x':
                fret_num = -1
            if isinstance(fret_num, str) or fret_num < -1:
                raise ValueError("Invalid fret_num. Use -1 or 'x' for muted strings.")
            elif fret_num > -1:
                # print(f"i={i}, fret_num={fret_num}, accidental={accidental}")
                notes.append(self.fret(i, fret_num, accidental))
            i -= 1

        print(notes)
        return nc.notes_to_chord(notes, quiet)


STANDARD = ("E2", "A2", "D3", "G3", "B3", "E4")
DROP_D = ("D2", "A2", "D3", "G3", "B3", "E4")
DADGAD = ("D2", "A2", "D3", "G3", "A3", "D4")
OPEN_D = ("D2", "A2", "D3", "F#3", "A3", "D4")

def add_guitar(
        name: str,
        tuning: tuple[str, ...],
        default: bool = False,
) -> Guitar:
    gr.add_guitar_record(name, list(tuning), default=default)
    return Guitar(name=name, tuning=tuning)


def load_guitar(name: str) -> Guitar:
    record = gr.get_guitar_record(name)
    return Guitar(name=name, tuning=record["tuning"])


def list_guitars() -> list[str]:
    return gr.list_guitar_names()


def remove_guitar(name: str) -> None:
    gr.remove_guitar_record(name)


def set_default_guitar(guitar: Guitar | str) -> Guitar:
    name = guitar if not isinstance(guitar, Guitar) else guitar.name
    gr.set_default_guitar_name(name)  # see guitar_registry.py
    return load_guitar(name)


def get_default_guitar() -> Guitar:
    registry_default = gr.get_default_guitar_name()
    if registry_default is None:
        raise ValueError("Default guitar not set.")
    return load_guitar(registry_default)


def get_tuning(high_to_low: bool = True, guitar: Guitar | None = None) -> None:
    if guitar is None:
        guitar = get_default_guitar()
    guitar.get_tuning(high_to_low)


def fret(
        guitar_string: int,
        fret_num: int,
        accidental: str = "sharp",
        guitar: Guitar | None = None,
) -> str:
    if guitar is None:
        guitar = get_default_guitar()
    return guitar.fret(guitar_string, fret_num, accidental)


def fret_notes(
        fret_nums: tuple[str|int, ...],
        accidental: str = "sharp",
        guitar: Guitar | None = None,
) -> str:
    if guitar is None:
        guitar = get_default_guitar()
    return guitar.fret_notes(fret_nums, accidental)


def main() -> None:
    print("Hello from g-to-c!")
    print()
    default_name = gr.get_default_guitar_name()
    print(f"Default guitar: {default_name}")
    get_tuning()


if __name__ == "__main__":
    main()
