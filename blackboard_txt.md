# Import TXT into Blackboard directly

## New Lines
New lines cannot be placed in TXT file. Have to combine all lines
and replace new lines with `<br />`.

## Unicode

Unicode characters are fine. Tested with UTF-8 encoding. 

Example:

```
What is 2<sup>1</sup>&middot;&pi;? π works, too.
```

## HTML 

HTML code can be placed in Questions, including SVG pictures.

## Escaping `[`

Only FIB\_PLUS questions require `[` be escaped, like `\[`. Othewise, 
it indicates a blank. 

