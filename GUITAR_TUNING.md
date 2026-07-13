# Tuning Confusion

"E2", "A2", "D3", "G3", "B3", "E4".  
These are the 6 strings of a guitar in standard tuning, or EADGBE.  
"E2" is the lowest in pitch.  
"E2" is also called string 6, or the "low-E string".  
"E4" is the highest in pitch.  
"E4" is also called string 1, or the "high-E string".  
When displaying tabs, they put the high-E string (string 1) on the TOP.  
When displaying tabs, they put the low-E string (string 6) on the BOTTOM.  
However, some silly people call the low-E string the "top string".  
Confused? Me too.  

In programming, everything is left-to-right, top-to-bottom, index 0 to len(list) - 1.  

When you create a tuning, you would do something like this:  

```python
DADGAD = Tuning(("D2", "A2", "D3", "G3", "A3", "D4"))
```

This is the low-to-high order, and it makes sense when read from left to right.  
Check out this useful one-liner.

```python
ac = add_guitar("acoustic", DADGAD)
```

This will create a new guitar, give it a name, a tuning, and assign it to a variable to use later.  
Now this gets passed to the registry, where you can see the tuning in guitars.json.  

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

The list maintains the low-to-high order, but now you're reading it from top-to-bottom.  
The Tuning data class also maintains this low-to-high order. The only time it needs to be reversed is when it is diplayed, which is handled in 
