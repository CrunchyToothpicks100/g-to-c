# g-to-c (CLI version)

A music theory tool for guitarists. You can take any guitar chord on any
tuning and convert it to chord notation. The chord notation loosely follows
the rules of jazz harmony, with consideration for edge cases (i.e. very
weird chords).

JSON files are used for storing guitars and tunings.

Interaction currently requires the Python REPL, or IPython: `ipython -i src/main.py`

## Project Status

Core logic is finished! Outputs are verbose and accurate!

## Migration to a webapp

This is a note-to-self.

- Migrate the python logic into a Django webapp (separate repo)
- The JSON logic will be replaced with ORM logic (will use SQLite)
- Create a webpage with a clickable fretboard

## MVP

Create an interactive tool (CLI? desktop app?)  
Store Guitars and tunings in a file (JSON or sqlite?)  
Select your guitar  
Convert frets to notes  
Convert finger positions to chords (A#maj7add9)  

## Current flow

The current implementation is a Python module backed by `data/guitars.json`:

1. Define a tuning as a tuple of note strings in low-to-high pitch order.
   `main.py` includes `STANDARD`, `DROP_D`, `DADGAD`, and `OPEN_D` examples.
2. Register the tuning with `add_guitar(name, tuning)`.
   The first registered guitar becomes the default automatically; pass
   `default=True` to explicitly make a guitar the default.
3. The guitar record is saved to `data/guitars.json`. Use `list_guitars()`,
   `load_guitar(name)`, `set_default_guitar(...)`, or `remove_guitar(name)` to
   manage the registry.
4. Call `get_default_guitar()` explicitly, or omit the `guitar` argument from
   `get_tuning()`, `fret()`, and `fret_notes()` to use the configured default.
5. Call `fret(guitar_string, fret_num)` to convert one fret position to a
   note. String 1 is the high string, and `len(tuning)` is the low string.
6. Call `fret_notes(fret_nums)` to convert a complete voicing to notes and
   chord notation. Provide one fret value per string in low-to-high tuning
   order; use `-1` or `"x"` for a muted string.

`get_tuning()` prints high-to-low (the usual tab display order) by default.
Pass `high_to_low=False` to print low-to-high.

Example:

```python
import main

main.add_guitar(
    "seven_string",
    ("B1", "E2", "A2", "D3", "G3", "B3", "E4"),
    default=True,
)
print(main.fret(6, 3))  # uses the default guitar
g = main.load_guitar("seven_string")
print(g.fret(7, 5))
print(main.fret_notes(("x", 0, 3, 2, 1, 1, 0), guitar=g))
```

## Tuning

"E2", "A2", "D3", "G3", "B3", "E4".  
These are the 6 open strings of a guitar in standard tuning, or EADGBE.  
"E2" is the lowest in pitch. "E4" is the highest in pitch.  
String 1, or the "high-E" string, plays the "E4" note.
String 6, or the "low-E string", plays an "E2" note.
When displaying tabs, they put the high-E string (string 1) on the TOP.  
When displaying tabs, they put the low-E string (string 6) on the BOTTOM.  

When you create a tuning, you would create a tuple like this:  

```python
DADGAD = ("D2", "A2", "D3", "G3", "A3", "D4")
```

This is the low-to-high order, and it makes sense when read from left to
right. Check out this useful one-liner.

```python
ac = main.add_guitar("acoustic", DADGAD)
```

This will create a new guitar, give it a name, a tuning, and assign it to
a variable to use later. Now this gets passed to the registry, where you
can see the tuning in guitars.json.

```JSON
    "acoustic": {
      "tuning": [
        "D2",
        "A2",
        "D3",
        "G3",
        "A3",
        "D4"
      ]
    },
```

The list maintains the low-to-high order, but now you're reading it from
top-to-bottom. Whenever `fret()` is called, the `guitar_string` parameter
represents the conventional string number. This has to be converted to the
correct index to find the string. For `fret(guitar_string=6, fret_num=3)`,
we can do len(self.tuning) - guitar_string, which gives us 0. When `guitar_string=1`,
6 - 1 = 5.
