#!/usr/bin/python3 -u
import sqlite3
import numpy as np
from optparse import OptionParser

class AnalysisBase:
    def __init__(self, stock, database):
        self.db = sqlite3.connect(database)


def main():
    parser = OptionParser()

    parser.add_option("-t", "--ticker",
                action="store", dest="ticker",
                help="Stock ticker")
    parser.add_option("--db", "--database",
                action="store", dest="database",
                help="Finance database, which is save by msfinance")

    (opts, args) = parser.parse_args()

    ticker_analysis = AnalysisBase(opts.ticker, opts.database)


if __name__ == '__main__':
    main()



