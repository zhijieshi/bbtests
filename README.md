# Blackboard Tests

Here are some tools for uploading questions into Blackboard LMS Original View. 

## Blackboard versions

Blackbaord learn currently supports two views: Original View and Ultra View. 
The Original View supports 

* Uploading questions in TXT files into tests/quizzes, or into a pool.

* Uploading questions through Respondus 4.0

* Importing questions in QTI packages into pools

* Importing questions exported from Blackboard

The Ultra View has very limited support for importing/uploading questions.
Basically, it can only import questions into qustion banks and the questions
must be exported from Blackboard. 

## Tools and File Format

## Built-in support

Blackboard supports uploading questions into tests/pools directly. The file
format must be tab delimited files. Excel can export sheets in this format. 

* Fields are separated by TABs.

* Fields are not in double quotations. 

* Fields can have HTML tags.

* Fields cannot have new lines, because double quotations are not
  supported. HTML tag `<br />` seems working fine. 

* Files can be in UTF-8.

Images are not supported. However, we can embed SVG files directly in fields.


## Respondus 4.0

Repsondus 4.0 can import questions from text files or Word documents.
It works well with questions with simple formatting.

The issues include:
    
* Does not support Unicode in text files.
* Does not support HTML code well. HTML blocks are stored in external files. 

## Other tools

* [BlackboardQuizMaker](https://github.com/toastedcrumpets/BlackboardQuizMaker)

* [text2qti](https://github.com/gpoore/text2qti)

  QTI does not support fill-in-multiple-blanks questions.

* [txt2qti](https://github.com/sfaroult/txt2qti). Convert text files to
  QTI format. The text files can be in Respondus format or Aiken format. 
