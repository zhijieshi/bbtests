# File format

`convert-to-txt.py` converts questions in text files in a more readable format
to the TAB delimited format that can be uploaded to Blackboard (Original View).
Although better file extensions for TAB delimited firles are `.tsv` or `.tab`,
Blackboard only accepts `.txt`. As a result, both input and output files have
the `.txt` extension.

The detailed description of the file format supported by Blackboard is on
[Blackboard's help page](https://help.blackboard.com/Learn/Instructor/Tests_Pools_Surveys/Reuse_Questions/Upload_Questions)

For simple questions, it is fine to prepare them in Excel and then exports to a
TAB delimited TXT file. It is hard if the question is long. The main difficulty
is that Blackboard does not support quoted fields and does not have a general
escape methods. So newlines and TABs cannot appear in any fields. To write a
question that has multiple lines, we have to separat lines by HTML tag `<br />`.

Respondus 4.0 supports a better file format. However, it also has many
limitations.

## Input text file

The input text file roughly follows what Respondus 4.0 accepts.

### General structure

* A question starts with a question number, followed by `.` or `)` and then a
  space. The question number is not important. All question numbers can be 1.
  Acutally, the question numbers are not preserved in output file.

* Respondus supports many options before a question, for example, `Points:`,
  `Title:`, etc. `convert-to-tsv` only recognizes `Type:`, which specifies the
  type of the question. The supported types are:

    * Multipel choices. "MC"
    * True/false. "TF"
    * Fill-in-the-bloank. "FIB" or "F"
    * Fill-in-multiple-blanks. "FIB\_PLUS" or "FMB".
    * Essay. "ESS" or "E"

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

The following is an example of a set of questions.

```
Type: TF
1. The Sun rises in the east. 

*a. True
b. False

Type: MC
1. What is 1 + 1?

*a. 0
b. 1
c. 2
d. 3

Type: FIB

1. What is 2<sup>3</sup>?

a. 8

Type: FMB

1. The Sun rises in the [east] and sets in the [west].

```

### Unicode

Unicode characters can appear in TXT files, at least in UTF-8 encoding. 
For example, 

```
What is 2<sup>1</sup>&middot;&pi;? π works, too.
```

### HTML 

HTML code can appear in questions and answers. So we can embed SVG pictures in
quetions. 

`convert-to-tsv` does not touch HTML tags. 

### Fill-in-multipe-blanks (FMB) quetions

In FMB questions, a `[` and `]` pair indicates a blank. The answers are placed
in brackets, for example, `[answer1, answer2]`. We need to escape `[`, i.e., 
write `\[`, if we do not want a blank after `\[`. 

`convert-to-tsv` only recognizes `[` as a blank when it is after a space or at 
the beginning of a line. It escapes other `[`'s.  For example,

```
This is a [blank] because '[' is after a space.

A[i] is not recognized as a blank. The '[' in A[i] is escaped. 
```

Only FMB questions require escaping `[`. 

### Code

Code can be placed in `<pre>` and `</pre>`. For example, 

```
<pre>
int   a[100];      // C code
addi  x1, x0, 0    // RISC-V instructions
</pre>
```

### Math

Blackboard does not support math equations well. There are a few ways to 
include math equations.  

* Use Unicode or HTML code to write simple equations

* Use MathJax. See the example in [`q-math.txt`](examples/q-math.txt)

* Convert math equations to SVG figures

* Use MathML, although it is only supported in Firefox
