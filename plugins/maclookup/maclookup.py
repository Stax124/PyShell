from yapsy.IPlugin import IPlugin
from functions import functions
import csv
import argparse
import tabulate


def maclookup(shell, *querry):
    parser = argparse.ArgumentParser()
    parser.add_argument("mac", help="Mac address of device",
                        nargs="?", default=None)
    try:
        args = parser.parse_args(querry)
    except SystemExit:
        return

    with open('plugins/maclookup/mac.csv', newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        table = []
        for row in reader:
            table.append((row['oui'], row['companyName'], row['countryCode']))

    if args.mac:
        mac = str(args.mac).upper()
        for item in table:
            if mac.startswith(item[0]):
                print(item)
                return
    else:
        print(tabulate.tabulate(table, headers=["MAC", "Company", "Country"]))


class PluginOne(IPlugin):
    def main(self):
        functions["maclookup"] = maclookup
