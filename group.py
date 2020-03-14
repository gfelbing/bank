#! /usr/bin/env python3

import os
from tabulate import tabulate
import csv
import argparse
import parse
import glob


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
        key = fdesc(entry)
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
        return topic[:total-3] + "..."
    else:
        return topic

if __name__ == "__main__":
    args = readargs()

    csv_files = []
    for fs in map(glob.iglob, args.csv):
        csv_files += list(fs)
    for csv_file in csv_files:
        parsed_csv = parse.parse(csv_file)
        print("# Auswertung für {} über Zeitraum {}".format(parsed_csv.source, parsed_csv.time_range))
        print()

        parsed_entries = parsed_csv.entries
        inbound, outbound = balance(parsed_entries)
        print("Während des Zeitraums wurden {} eingezahlt und {} ausgegeben.".format(
            famount(inbound),
            famount(outbound)
        ))
        print()

        print("Gruppiert nach Referenz und sortiert nach Betrag:")
        print()
        grouped = group_entries(parsed_entries)
        sorted_groups = sorted(grouped, key=lambda x: grouped[x]['sum'])
        for key in sorted_groups:
            group = grouped[key]
            print("- {}: {}".format(key[:50], famount(group['sum'])))
            for entry in group['entries']:
                print("  - {}: {}".format(entry['date'], famount(entry['amount'])))
        print()

        print("Alle Transaktionen nach Zeit")
        print()
        table_entries = [ [ e['date'], famount(e['amount']), fdesc(e) ] for e in parsed_entries ]
        print(tabulate(table_entries, headers=['Datum', 'Betrag', 'Beschreibung']))
        print()
        print()
