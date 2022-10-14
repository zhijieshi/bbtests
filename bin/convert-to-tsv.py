# import system module
import sys, argparse, csv
from string import Template
from enum import Enum, auto
import re
import fileinput
import logging

# wrapper 
class FileWrapper:
    def __init__(self, file):
        self.file = file
        self.buffer = None
        
    def readline(self):
        if self.buffer is None:
            rv = self.file.readline()
            if rv == '':
                logging.debug("End of file")
                return None
            rv = rv.strip()
        else:
            rv = self.buffer
            self.buffer = None
        return rv 
        
    def unreadline(self, line):
        assert self.buffer is None
        self.buffer = line

class   LineState(Enum):
    EMPTY = auto()
    PARA = auto()
    CODE = auto()

class   QType(Enum):
    MC = auto()
    TF = auto()
    FIB = auto()
    FIB_PLUS = auto()
    ESS = auto()
    NUM = auto()
    F = FIB

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

# this function detects if the line might be a start of a new question  
def     is_new_question(line):
    m = re.match(r'(Type:|Points:|Title:|\d+\.) ', line)
    return m is not None

# classes for questions
class   Question:

    def __init__(self, t):
        self.type = t
        self.description = []
        self.answers = []
        self.linebreak = '<br />'
        self.para_start = "<p>"
        self.para_end = "</p>"
        self.code_start = '<pre class="language-python">'
        self.code_end = "</pre>"
        pass

    def add_description(self, d):
        # simply append the line to self.description 
        # will clean up later when get_description() is called
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
        for line in self.description :
            if state == LineState.PARA:
                if not line:
                    d += self.para_end
                    state = LineState.EMPTY
                elif line in ("<pre>", "```"): 
                    d += self.para_end + self.code_start
                    state = LineState.CODE
                else:
                    d += ' ' + line
            elif state == LineState.EMPTY:
                if line in ("<pre>", "```"): 
                    d += self.code_start
                    state = LineState.CODE
                elif line:
                    # TODO: support other HTML code?
                    d += self.para_start + line
                    state = LineState.PARA
                else:
                    d += self.para_start + self.para_end
            else: # in code
                if line in ("</pre>", "```"): 
                    d += self.code_end
                    state = LineState.EMPTY
                else:
                    d += line + self.linebreak
        if state == LineState.CODE:
            logging.error("Code block did not end.")
            exit(2)
        elif state == LineState.PARA:
            d += self.para_end
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
            # temporarily disable multiple answers, as we need ',' in answers
            # [self.add_answer(x.strip()) for x in m.group(2).split(',')]
            self.add_answer(m.group(2))
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
            # find variables
            # a variable must be after a space or at the beginning of a line
            tmp = re.sub(r'(^| )\[([^]]+)]', process_answer, line)
            # escape empty brackets " []" 
            tmp = re.sub(r'(^| )\[]', r'\1\\[]', tmp)
            # escape other '['
            self.description[index] = re.sub(r'(\S)(\[)', escape_bracket, tmp)

    def add_answer(self, answer):
        self.answers.append(answer)
        
    def get_answer_list(self):
        return self.answers

def     load_description(q, file, has_answer):
    line = file.readline()
    q.add_description(line)
    empty_line = False
    while True:
        line = file.readline()

        if line is None: # end of file
            return

        # if the last line is empty, check if this line 
        # starts the answers or starts a new questin
        if empty_line:  
            # look ahead
            if (has_answer and is_answer(line)
                or not has_answer and is_new_question(line)):
                file.unreadline(line)
                return

        empty_line = is_empty(line)
        q.add_description(line)

def     load_answers(q, file):

    while True:
        line = file.readline()
        if line is None:
            return
        elif is_answer(line):
            q.add_answer(line)
        elif not is_empty(line):
            file.unreadline(line)
            return

def     load_question(q, file, has_answer = True):
    load_description(q, file, has_answer)
    if has_answer:
        load_answers(q, file)

# parse the arguments
parser = argparse.ArgumentParser(description='Python Example')
parser.add_argument('inputfile', nargs='+', help='Input files')
parser.add_argument("--output", "-o", help="Output file")
parser.add_argument("--encoding", default="utf-8", 
        choices=["utf-8", "utf-8-sig", "utf-16"],
        help="Input file encoding")
parser.add_argument("-v", action='store_true', default=False) 

args = parser.parse_args()

if (args.v):
    print(args)


logging.basicConfig(level=logging.INFO)

questions = []

qtype = QType.MC
# with open(args.inputfile, 'r', encoding='utf-8') as f:
try:
    with fileinput.FileInput(files=args.inputfile, 
            mode='r', 
            openhook=fileinput.hook_encoded(args.encoding)) as f:
        fw = FileWrapper(f) 
        while True: 
            line = fw.readline()
            if line is None:
                break
<<<<<<< HEAD
            if m := re.match(r"Type:\s*(F|FIB|MC|FIB_PLUS|FMB|E|ESS)\s*$", line):
=======
            logging.debug(f"'{line}'")
            if m := re.match(r"Type:\s*(F|FIB|NUM|MC|FIB_PLUS|FMB|E|ESS)\s*$", line):
>>>>>>> 376be489d260f33789a8aa9b0cd1b7206737d4f8
                qtype = Str2QType[m.group(1)]
                logging.debug(f"Question type:{m.group(1)}")
            elif m := re.match(r"(\d+)\.\s+(.+)", line): 
                fw.unreadline(line)
                if qtype in [QType.FIB, QType.F, QType.NUM]:
                    q = FIBQuestion() 
                    load_question(q, fw)
                elif qtype == QType.MC:
                    q = MCQuestion() 
                    load_question(q, fw)
                elif qtype == QType.TF:
                    q = TFQuestion() 
                    load_question(q, fw)
                elif qtype == QType.FIB_PLUS:
                    q = FMBQuestion() 
                    load_question(q, fw, False)
                    q.find_answers()
                else:
                    raise ValueError("Unsupported type." + t)
                questions.append(q)
                logging.debug(f"End of a question.")
            elif is_new_question(line):
                # these are additonal features that are not supported
                pass
            elif is_empty(line):
                pass
            else:
                logging.error(f"Unknown lines: {line}")
except FileNotFoundError as e:
    print(e)
    exit(1)

if not args.output:
    for q in questions:
        q.cleanup_description()
        print(q.type.name)
        print(q.get_description())
        print(q.get_answer_list())
else:
    # the default encoding is utf-8
    with open(args.output, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
        for q in questions:
            q.cleanup_description()
            fields = [q.type.name, q.get_description()]
            fields.extend(q.get_answer_list())
            csvwriter.writerow(fields)
