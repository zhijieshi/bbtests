# File format

## TXT files supported by Blackboard 

### New Lines
New lines cannot be placed in TXT file. Have to combine all lines
and replace new lines with `<br />`.

### Unicode

Unicode characters are fine. Tested with UTF-8 encoding. 

Example:

```
What is 2<sup>1</sup>&middot;&pi;? π works, too.
```

### HTML 

HTML code can be placed in Questions, including SVG pictures.

### Escaping `[`

Only FIB\_PLUS questions require `[` be escaped, like `\[`. Othewise, 
it indicates a blank. 

## convert-to-txt.py

The input text file roughly follows what Respondus 4.0 accepts.

* `Type:` specifies the type of the question. 

* `Points:`, and `Title:` are optional. They are ignored. 

* A question starts with a question number, followed by `. ` or `) `. Note
  there is space.

* There must be an empty line between question and answers.
  Fill-in-multiple-blanks questions do not have answer section.

* An answer starts with a letter, followed by `. ` or `) `. Note there is a
  space. The correct answer starts with a `*`. 

  ```
  a. A Wrong answer
  *b. The correct answer
  ```
* An answer must be placed in one line. There is no empty line between answers. 

* There must be an empty line between question/answer and the next question.

