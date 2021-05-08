# import system module
import sys, argparse, csv
from string import Template

# parse the arguments
# more examples at https://pymotw.com/2/argparse/
parser = argparse.ArgumentParser(description='Python Example')
parser.add_argument('templatefile', help='template file')
parser.add_argument('csvfile', help='csv file')
# example: -o a.txt
parser.add_argument("-o", "--output", help="File to be updated")
# boolean option, short only
parser.add_argument("-v", action='store_true', default=False) 

args = parser.parse_args()

print(args)

tmpl_str = ''

with open(args.templatefile, 'r', encoding='utf-8') as f:
    tmpl_str = f.read()

print(tmpl_str)
tmpl = Template(tmpl_str)

with open(args.csvfile, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        q = tmpl.safe_substitute(row)
        print(q)

