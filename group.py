#! /usr/bin/env python3

import os
from tabulate import tabulate
import csv
import argparse
import parse
import glob
import re
from group_defs import groups

def balance(entries):
    inbound=0
    outbound=0
    for entry in entries:
        amount=entry['amount']
        if amount > 0:
            inbound += amount
        else:
            outbound -= amount
    return inbound, outbound

def group_entries(entries):
    result = {}
    for entry in entries:
        key = get_group(entry)
        if key in result:
            result[key]['sum'] += entry['amount']
            result[key]['entries'].append(entry)
        else:
            result[key] = {
                    'sum': entry['amount'],
                    'entries': [entry]
            }
    return result

def famount(amount):
    return "{:1.2f}€".format(amount)

def readargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs='+')
    return parser.parse_args()

def fdesc(entry):
    total = 80
    topic = entry['topic']

    if len(topic) > total:
        topic = topic[:total-3] + "..."

    return topic

def get_group(entry):
    topic = fdesc(entry)
    for regex, group in groups.items():
        if re.match(regex, topic):
            return group
    return topic


if __name__ == "__main__":
    args = readargs()

    csv_files = []
    for fs in map(glob.iglob, args.csv):
        csv_files += list(fs)

    print("# Banking analysis")
    print()
    print("The following CSVs where analysed: ")
    print()
    parsed_entries = []
    for csv_file in csv_files:
        parsed_csv = parse.parse(csv_file)
        print("- {}, {}".format(parsed_csv.source, parsed_csv.time_range))
        parsed_entries += parsed_csv.entries
    print()

    inbound, outbound = balance(parsed_entries)
    print("There was {} inbound and {} outbound.".format(
        famount(inbound),
        famount(outbound)
    ))
    print()

    print("## Grouped transactions:")
    print()
    grouped = group_entries(parsed_entries)
    sorted_groups = sorted(grouped, key=lambda x: grouped[x]['sum'])
    for key in sorted_groups:
        group = grouped[key]
        print("- {}: {}".format(key[:50], famount(group['sum'])))
        for entry in group['entries']:
            print("  - {}: {}: {}".format(entry['date'], famount(entry['amount']), entry['topic'][:50]))
    print()

    print("## All transactions by time")
    print()
    table_entries = [ [ e['date'], famount(e['amount']), fdesc(e) ] for e in parsed_entries ]
    print(tabulate(table_entries, headers=['Datum', 'Betrag', 'Beschreibung']))
    print()
    print()
