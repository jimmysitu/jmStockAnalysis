#!/usr/bin/python3 -u
import sqlite3
import pandas as pd
import numpy as np
from optparse import OptionParser

class AnalysisBase:
    def __init__(self, database, ticker, exchange=None):
        self.db = sqlite3.connect(database)

        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'aapl%'"
        self.tables = pd.read_sql_query(query, self.db)

        for table in self.tables['name']:
            print(table)

    def cash_flow_ratio(self, ticker, exchange):
        '''
        现金流动负债比率
        Cash Flow Ratio = Operating Cash Flow / Current Liabilities

        Args:
        Returns:
        '''
        pass

    def cash_flow_adequancy_ratio(self, ticker):
        '''
        '''
        pass

    def cash_reinvestment_ratio(self, ticker):
        '''
        '''
        pass

    def cash_to_total_assets_ratio(self, ticker):
        '''
        '''
        pass




def main():
    parser = OptionParser()

    parser.add_option("-t", "--ticker",
                action="store", dest="ticker",
                help="Stock ticker")
    parser.add_option("--db", "--database",
                action="store", dest="database",
                help="Finance database, which is saved by msfinance")

    (opts, args) = parser.parse_args()

    ticker_analysis = AnalysisBase(opts.database, opts.ticker)


if __name__ == '__main__':
    main()



