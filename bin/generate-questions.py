# import system module
import sys, argparse, csv
from string import Template

# parse the arguments
parser = argparse.ArgumentParser(description='Generate questions from a template.')
parser.add_argument('templatefile', help='template file')
parser.add_argument('csvfile', help='csv file')
# parser.add_argument("--output", "-o", help="output filename")
parser.add_argument("--encoding", default="utf-8", 
        choices=["utf-8", "utf-8-sig", "utf-16"],
        help="the encoding of input files.")
parser.add_argument("-v", action='store_true', default=False) 

args = parser.parse_args()

if args.v:
    print(args)

tmpl_str = ''

with open(args.templatefile, 'r', encoding=args.encoding) as f:
    tmpl_str = f.read()

if args.v:
    print(tmpl_str)

tmpl = Template(tmpl_str)

with open(args.csvfile, 'r', encoding=args.encoding, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        q = tmpl.safe_substitute(row)
        print(q)

