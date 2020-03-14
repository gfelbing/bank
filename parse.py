import csv
import os
from babel.numbers import parse_decimal
import tempfile

basedir=os.path.dirname(os.path.realpath(__file__))

class ParsedResult:
    def __init__(self, source, time_range, entries):
        self.source = source
        self.time_range = time_range
        self.entries = list(entries)


def parse(file):
    with tempfile.NamedTemporaryFile(suffix='.csv',dir="{}/tmp".format(basedir)) as utf8_file:
        # thanks dkb. even with bad encoding, you screwed it up.
        os.system("iconv -f iso-8859-1 -t utf-8 -c {} -o {}".format(file, utf8_file.name))
        os.system("sed -i 's/\\x0//g' {}".format(utf8_file.name))
        with open(utf8_file.name, "r") as f:
                reader = csv.reader(f, delimiter=';', quotechar='"')
                head = next(reader)
                type = head[0]
                if type == "Kreditkarte:":
                    return parse_creditcard(head[0] + head[1], f)
                elif type == "Kontonummer:":
                    return parse_giro(head[0] + head[1], f)
                raise Exception("Unknown type '{}'".format(type))

def parse_timerange(reader):
    row = next(reader)
    time_range = ""
    if row[0] == "Zeitraum:":
        time_range = row[1]
    elif row[0] == "Von:":
        range_to = next(reader)[1]
        time_range = "{} - {}".format(row[1], range_to)
    return time_range

def famount(str_amount):
    return parse_decimal(str_amount, locale='de')

def parse_creditcard(source, f):
    reader = csv.reader(f, delimiter=';', quotechar='"')
    next(reader) # skip empty line
    time_range = parse_timerange(reader)
    row = next(reader)
    while len(row)>0:
        row = next(reader)

    reader = csv.DictReader(f, delimiter=';', quotechar='"')
    entries = []
    for row in reader:
        entries.append({
                "date": row["Belegdatum"],
                "amount" : famount(row["Betrag (EUR)"]),
                "topic": row["Beschreibung"],
                "desc": row["Ursprünglicher Betrag"]
        })
    
    return ParsedResult(source, time_range, entries)

def parse_giro(source, f):
    reader = csv.reader(f, delimiter=';', quotechar='"')
    next(reader) # skip empty line
    time_range = parse_timerange(reader)
    row = next(reader)
    while len(row)>0:
        row = next(reader)

    reader = csv.DictReader(f, delimiter=';', quotechar='"')
    entries = []
    for row in reader:
        reference = row["Verwendungszweck"].split("<br />")
        entries.append({
                "date": row["Buchungstag"],
                "amount" : famount(row["Betrag (EUR)"]),
                "topic": reference[0],
                "desc": " ".join(reference[1:])
        })
    
    return ParsedResult(source, time_range, entries)
