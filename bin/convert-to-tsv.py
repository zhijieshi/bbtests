# import system module
import sys, argparse, csv
from string import Template
from enum import Enum, auto
import re

# wrapper 
class FileWrapper:
    def __init__(self, file):
        self.file = file
        self.buffer = None
        
    def readline(self):
        if self.buffer is None:
            return self.file.readline()
        rv = self.buffer
        self.buffer = None
        return rv 
        
    def unreadline(self, line):
        assert self.buffer is None
        self.buffer = line

class   LineState(Enum):
    EMPTY = auto()
    PARA = auto()
    PRE = auto()

class   QType(Enum):
    MC = auto()
    TF = auto()
    FIB = auto()
    FIB_PLUS = auto()
    ESS = auto()
    NUM = auto()

Str2QType = {
        "MC" :  QType.MC,
        "TF" :  QType.TF,
        "F" :   QType.FIB,
        "FIB" : QType.FIB,
        "FIB_PLUS" : QType.FIB_PLUS,
        "FMB" : QType.FIB_PLUS,
        "NUM" : QType.NUM,
        "E" :   QType.ESS,
        "ESS" :   QType.ESS,
        }

def     is_empty(line):
    return not line or (line == "\n")

def     is_answer(line):
    m = re.match(r'(\*)?[a-z][.)] ', line)
    return m is not None

def     get_answer(line):
    m = re.match(r'(\*)?[a-z][.)] \s*(.+)', line)
    assert m is not None
    return (m.group(2), m.group(1) == '*') 

def     is_new_question(line):
    m = re.match(r'(Type: |Points: |Title: |\d+\. )', line)
    return m is not None

# classes for questions
class   Question:

    def __init__(self, t):
        self.type = t
        self.description = []
        self.answers = []
        pass

    def add_description(self, d):
        self.description.append(d)

    def add_answer(self, a):
        self.answers.append(get_answer(a))

    def cleanup_description(self):
        m = re.match(r'\d+[.)]\s+(.+)$', self.description[0])
        self.description[0] = m.group(1)

        while is_empty(self.description[-1]):
            self.description.pop()

    def get_description(self):
        d = ''
        state = LineState.EMPTY
        LINEBREAK = '<br />'
        for line in self.description :
            if state == LineState.PARA:
                stripped = line.strip()
                if not stripped:
                    d += LINEBREAK
                    state = LineState.EMPTY
                elif stripped in ("<pre>", "```"): 
                    d += LINEBREAK + '<pre>'
                    state = LineState.PRE
                else:
                    d += ' ' + stripped
            elif state == LineState.EMPTY:
                stripped = line.strip()
                if not stripped:
                    pass    # Only one LINEBREAK for consecutive empty lines
                elif stripped in ("<pre>", "```"): 
                    d += LINEBREAK + '<pre>'
                    state = LineState.PRE
                else:
                    d += stripped
                    state = LineState.PARA
            else: # in pre tags
                stripped = line.rstrip()
                if stripped in ("</pre>", "```"): 
                    stripped = '</pre>'
                    state = LineState.EMPTY
                d += stripped + LINEBREAK
        return d

# Multiple-choice 
class   MCQuestion(Question):

    def __init__(self):
        super().__init__(QType.MC)

    def get_answer_list(self):
        # [ _ for t in self.answers for _ in t]
        l = [] 
        for (a, c) in self.answers:
            t = 'Correct' if c else 'Incorrect'
            l.extend([a, t])
        return l

# True/False
class   TFQuestion(Question):

    def __init__(self):
        super().__init__(QType.MC)

    def get_answer_list(self):
        if self.answers[0][1] or not self.answers[1][1]:
            return ['True']
        return ['False']

# Fill-in-the-blank
class   FIBQuestion(Question):

    def __init__(self):
        super().__init__(QType.FIB)

    def get_answer_list(self):
        return [ a for (a, c) in self.answers]

# Fill-in-multiple-blanks
class   FMBQuestion(Question):

    def __init__(self):
        super().__init__(QType.FIB_PLUS)

    def find_answers(self):

        counter = 0

        def process_answer(m):
            nonlocal counter
            varname = 'var' + str(counter)
            counter += 1
            # print(varname, m.group(0), f"'{m.group(2)}'")
            if counter > 1:
                self.add_answer('')
            self.add_answer(varname)
            [self.add_answer(x.strip()) for x in m.group(2).split(',')]
            return f'{m.group(1)}[{varname}]'

        def escape_bracket(m):
            # print(m.group(1), m.group(2))
            ESCAPE_CHAR = '\\'

            if m.group(1) == ESCAPE_CHAR:
                return m.group(0)

            return m.group(1) + ESCAPE_CHAR + m.group(2)

        # a blank must be on one line
        # a line can have multiple blanks
        for index, line in enumerate(self.description):
            # find variable
            tmp = re.sub(r'(^| )\[([^]]+)]', process_answer, line)
            # escape other '['
            self.description[index] = re.sub(r'(\S)(\[[^]]+])', escape_bracket, tmp)

    def add_answer(self, answer):
        self.answers.append(answer)
        
    def get_answer_list(self):
        return self.answers

def     load_description(q, file, has_answer):
    line = file.readline()
    # remove question number
    q.add_description(line)
    empty_line = False
    while True:
        line = file.readline()
        if not line:
            return
        if empty_line:
            # look ahead
            if has_answer and is_answer(line):
                file.unreadline(line)
                return
            elif is_new_question(line):
                file.unreadline(line)
                return
        empty_line = is_empty(line)
        q.add_description(line)

def     load_answers(q, file):
    while True:
        line = file.readline()
        if is_answer(line):
            q.add_answer(line)
        else:
            file.unreadline(line)
            return

def     load_question(q, file, has_answer):
    load_description(q, file, has_answer)
    if has_answer:
        load_answers(q, file)

# parse the arguments
parser = argparse.ArgumentParser(description='Python Example')
parser.add_argument('inputfile', help='input file')
parser.add_argument("--output", "-o", help="File to be updated")
parser.add_argument("-v", action='store_true', default=False) 

args = parser.parse_args()

if (args.v):
    print(args)

questions = []

with open(args.inputfile, 'r', encoding='utf-8') as f:
    fw = FileWrapper(f) 
    qtype = QType.MC
    while True: 
        line = fw.readline()
        # print(line)
        if not line:
            break
        if m := re.match(r"Type:\s*(F|FIB|MC|FIB_PLUS|FMB|E|ESS)$", line):
            qtype = Str2QType[m.group(1)]
            if args.v: print("Question type:", t.name)
        elif m := re.match(r"(\d+)\.\s+(.+)", line): 
            fw.unreadline(line)
            if qtype == QType.FIB:
                q = FIBQuestion() 
                load_question(q, fw, True)
            elif qtype == QType.MC:
                q = MCQuestion() 
                load_question(q, fw, True)
            elif qtype == QType.TF:
                q = TFQuestion() 
                load_question(q, fw, True)
            elif qtype == QType.FIB_PLUS:
                q = FMBQuestion() 
                load_question(q, fw, False)
                q.find_answers()
            else:
                raise ValueError("Unsupported type." + t)
            questions.append(q)
            qtype = QType.MC
        elif is_new_question(line):
            pass
        else:
            if args.v: print("skipped:", line)

if not args.output:
    for q in questions:
        q.cleanup_description()
        print(q.type.name)
        print(q.get_description())
        print(q.get_answer_list())
else:
    with open(args.output, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
        for q in questions:
            q.cleanup_description()
            fields = [q.type.name, q.get_description()]
            fields.extend(q.get_answer_list())
            csvwriter.writerow(fields)
