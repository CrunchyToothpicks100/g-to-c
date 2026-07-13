# g-to-c

A music theory tool for guitarists.  
Currently uses JSON for storing guitars and tunings.  
Interaction currently requires the REPL, or IPython (recommended).  

## MVP

Create an interactive tool (CLI? desktop app?)  
Store Guitars and tunings in a file (JSON or sqlite?)  
Select your guitar  
Convert frets to notes  
Convert finger positions to chords (A#maj7add9)  

## Current flow

Current flow:

1. Create a `Tuning` object with a tuple of note strings.
   - Tuning tuples are stored low-to-high.
   - `tuning.strings(low_to_high=True)` gives the same low-to-high order for left-to-right display.
   - Example: `DADGAD = Tuning(("D2", "A2", "D3", "G3", "A3", "D4"))`
   - This is in `main.py`.

2. Create a `Guitar` with a name and that `Tuning`.
   - Example: `Guitar(name="acoustic", tuning=DADGAD)`

3. Register it with `add_guitar(...)`.
   - `add_guitar()` accepts either a `Tuning` or a raw tuple/list.
   - It writes the tuning into `guitars.json` through `guitar_registry.py`.
   - If `default=True`, it also sets that guitar as the default in the registry.

4. Read it back later with `load_guitar(name)` or use the default.
   - `get_default_guitar()` loads the default name from JSON every time and rebuilds the `Guitar`.
   - `get_tuning()` and `fret()` call `get_default_guitar()` if you don't pass a `Guitar`.
   - `get_tuning()` prints top-to-bottom high-to-low by default.
   - `get_tuning(low_to_high=True)` prints top-to-bottom low-to-high.

5. Get fret notes with `fret(guitar_string, fret_num, guitar=None)`.
   - `guitar_string=1` means the high string.
   - `guitar_string=len(tuning)` means the low string.
   - It picks the open string from the tuning.
   - Converts that note to a number with `note_to_num()`.
   - Adds the fret offset.
   - Converts back with `num_to_note()`.

Example:

```python
import main

main.add_guitar("seven_string", ("B1", "E2", "A2", "D3", "G3", "B3", "E4"), default=True)
print(main.fret(6, 3))  # uses the default guitar
g = main.load_guitar("seven_string")
print(g.fret(7, 5))
```
