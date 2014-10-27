# Reads an XML file, parses specified fields into a string,
# and outputs to a file.
#
# python xml_parse.py --help for info on cmd line arguments.

import re
import xml.etree.cElementTree as ET
import argparse

from printer import Printer

argparser = argparse.ArgumentParser()
argparser.add_argument("-i", "--input", dest="xml_file", help="XML input filename.")
argparser.add_argument("-o", "--output", dest="outfile", help="Output text filename.")
argparser.add_argument("-t", "--tag", dest="tag", default="row", help="XML tag to parse.")
argparser.add_argument("-f", "--fields", dest="fields", default=['Title', 'Body'], nargs="+", help="XML fields to parse.")
argparser.add_argument("-n", "--num_records", dest="num_records", type=int, default=27000000, help="Approx # lines in xml_file.")
args = argparser.parse_args()

TAG_RE = re.compile(r'<[^>]+>')
AN_RE = re.compile(r'[^a-zA-Z0-9\s]')

def clean(text):
    return ' '.join(AN_RE.sub('', TAG_RE.sub('', text)).strip().split())

def parse_and_write(xml_file, outfile, fields, tag, n):
    # get an iterable
    context = ET.iterparse(xml_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    i = 0
    with open(outfile, 'w') as f:
        for event, row in context:
            if event == "end" and row.tag == tag:
                if i % 100000 == 0:
                    pct = round((i * 1.0 / n) * 100, 1)
                    Printer("Processed {0} records. ~ {1}\% complete.".format(i, pct))
                if all(map(lambda x: x in row.attrib, fields)):
                    field_data = [clean(row.attrib[fd].encode('ascii', 'ignore')) for fd in fields]
                    text = " ".join(field_data) + "\n"
                    f.write(text)
                i += 1
                root.clear()

parse_and_write(args.xml_file, args.outfile, args.fields, args.tag, args.num_records)