from __future__ import annotations

from dataclasses import dataclass

import note_conversion as nc
import guitar_registry as gr


@dataclass
class Tuning:
    notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.notes, tuple):
            self.notes = tuple(self.notes)

        if not self.notes:
            raise ValueError("Tuning must contain at least one string")

    def strings(self, reverse: bool = False) -> tuple[str, ...]:
        return tuple(reversed(self.notes)) if reverse else self.notes

    def to_list(self) -> list[str]:
        return list(self.notes)

    @classmethod
    def from_iterable(cls, notes: tuple[str, ...] | list[str]) -> Tuning:
        return cls(tuple(notes))


@dataclass
class Guitar:
    name: str
    tuning: Tuning

    def get_tuning(self, reverse: bool = False) -> None:
        strings = self.tuning.strings(reverse=reverse)
        total_strings = len(strings)

        for index, note in enumerate(strings, start=1):
            string_number = index if not reverse else total_strings + 1 - index
            print(f"String {string_number}: {note}")

    def fret(self, guitar_string: int, fret_num: int) -> str:
        if guitar_string < 1 or guitar_string > len(self.tuning.notes):
            raise IndexError("guitar_string is out of range for this tuning")

        open_string = self.tuning.strings()[guitar_string - 1]
        open_note_num = nc.note_to_num(open_string)
        semitone = open_note_num + fret_num
        return nc.num_to_note(semitone)


DADGAD = Tuning(("D4", "A3", "G3", "D3", "A2", "D2"))
STANDARD = Tuning(("E4", "B3", "G3", "D3", "A2", "E2"))
DROP_D = Tuning(("E4", "B3", "G3", "D3", "A2", "D2"))
default_guitar: Guitar | None = None


def add_guitar(
    name: str,
    tuning: Tuning | tuple[str, ...] | list[str],
    default: bool = False,
) -> Guitar:
    tuning_obj = tuning if isinstance(tuning, Tuning) else Tuning.from_iterable(tuning)
    gr.add_guitar_record(name, tuning_obj.to_list(), default=default)
    guitar = Guitar(name=name, tuning=tuning_obj)
    if default or gr.get_default_guitar_name() == name:
        global default_guitar
        default_guitar = guitar
    return guitar


def load_guitar(name: str) -> Guitar:
    record = gr.get_guitar_record(name)
    return Guitar(name=name, tuning=Tuning.from_iterable(record["tuning"]))


def list_guitars() -> list[str]:
    return gr.list_guitar_names()


def remove_guitar(name: str) -> None:
    global default_guitar
    gr.remove_guitar_record(name)
    if default_guitar is not None and default_guitar.name == name:
        default_guitar = None


def set_default_guitar(name: str) -> Guitar:
    global default_guitar
    gr.set_default_guitar_name(name)  # see guitar_registry.py
    default_guitar = load_guitar(name)
    return default_guitar


def _resolve_default_guitar() -> Guitar:
    global default_guitar

    if default_guitar is not None:
        return default_guitar

    default_name = gr.get_default_guitar_name()
    if default_name is None:
        raise ValueError("Default guitar not set.")

    default_guitar = load_guitar(default_name)
    return default_guitar


def get_tuning(guitar: Guitar | None = None, reverse: bool = False) -> None:
    if guitar is None:
        guitar = _resolve_default_guitar()
    guitar.get_tuning(reverse=reverse)


def fret(
    guitar_string: int,
    fret_num: int,
    guitar: Guitar | None = None,
) -> str:
    if guitar is None:
        guitar = _resolve_default_guitar()
    return guitar.fret(guitar_string, fret_num)


def main() -> None:
    print("Hello from g-to-c!")
    get_tuning()

registry_default = gr.get_default_guitar_name()
if registry_default is not None:
    default_guitar = load_guitar(registry_default)


if __name__ == "__main__":
    main()
