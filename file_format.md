# File format

`convert-to-txt.py` converts questions in text files in a more readable format
to the TAB delimited format that can be uploaded to Blackboard (Original View).
Although better file extensions for TAB delimited firles are `.tsv` or `.tab`,
Blackboard only accepts `.txt`. As a result, both input and output filenames
may be `.txt` files.

## Input text file

The input text file roughly follows what Respondus 4.0 accepts.

* A question starts with a question number, followed by `.` or `)` and then a
  space. For example, 

```
1. This is a question.
```

* Options can be specified before each question. `Type:` specifies the type of
  the question. The accepted types are:

    * Multipel choices. "MC"
    * True/false. "TF"
    * Fill-in-the-bloank. "FIB" or "F"
    * Fill-in-multiple-blanks. "FIB\_PLUS" or "FMB".
    * Essay. "ESS" or "E"

For example, 

```
Type: TF

1. The Sun rises in the east. 

*a. True
b. False
```

* Respondus supports more options. `Points:`, and `Title:` are recognized and
  then ignored. 

* There must be an empty line between question and answers.
  Fill-in-multiple-blanks questions do not have the answer section.

* An answer starts with a letter, followed by `. ` or `) `. Note there is a
  space. The correct answer starts with a `*`. 

  ```
  a. A Wrong answer
  *b. The correct answer
  ```
* Each answer must be placed in one line. 

* There is no empty line between answers. 

* There must be an empty line between question/answer and the next question.

## TXT files supported by Blackboard 

The detailed description of the file format is on 
[Blackboard's help page](https://help.blackboard.com/Learn/Instructor/Tests_Pools_Surveys/Reuse_Questions/Upload_Questions)

The main limitation is Blackboard does not support quoted fields and 
does not have a general escape methods.  

### New Lines
New lines cannot be placed in TXT file. 

`convert-to-tsv` separates lines with `<br />`. 

### Unicode

Unicode characters are fine. Tested with UTF-8 encoding. 

Example:

```
What is 2<sup>1</sup>&middot;&pi;? π works, too.
```

### HTML 

HTML code can be placed in Questions, including SVG pictures. 

`convert-to-tsv` does not touch HTML tags. So it is more flexible than
Respondus 4.0.

### Escaping `[`

Only FIB\_PLUS questions require `[` be escaped, like `\[`. Othewise, 
it indicates a blank. 

