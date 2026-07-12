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

  1. Create a Tuning object with a tuple of note strings.
      - Example: `DADGAD = Tuning(("D4", "A3", "G3", "D3", "A2", "D2"))`
      - This is in main.py.

  2. Create a Guitar with a name and that Tuning.
      - Example: `Guitar(name="acoustic", tuning=DADGAD)`

  3. Register it with add\_guitar(...).
      - add\_guitar() accepts either a Tuning or a raw tuple/list.
      - It writes the tuning into guitars.json through guitar\_registry.py.
      - If default=True, it also sets that guitar as the default in the registry.

  4. Read it back later with load\_guitar(name) or use the default.
      - get\_tuning() and fret() call \_resolve\_default\_guitar()
        if you don't pass a Guitar.
      - That resolver loads the default name from JSON and rebuilds the Guitar.

  5. Get fret notes with fret(guitar\_string, fret\_num, guitar=None).
      - It picks the open string from the tuning.
      - Converts that note to a number with note\_to\_num().
      - Adds the fret offset.
      - Converts back with num\_to\_note().

Example:

```python
  import main

  main.add_guitar("seven_string", ("B3", "E3", "A2", "D2", "G2", "B2", "E2"), default=True)
  print(main.fret(6, 3))          # uses the default guitar
  g = main.load_guitar("seven_string")
  print(g.fret(7, 5))
```
