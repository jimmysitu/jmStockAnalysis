#!/usr/bin/python3 -u
import sqlite3
import pandas as pd
import numpy as np
from optparse import OptionParser

class AnalysisBase:
    '''
    对单一股票的分析基类，获取原始数据，计算各种指标
    '''
    def __init__(self, database, ticker, exchange=None):
        self.db = sqlite3.connect(database)

        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'aapl%'"
        tables = pd.read_sql_query(query, self.db)

        for table_name in tables['name']:
            query = f"SELECT * FROM {table_name}"

            # 保存三大财报原始数据，DataFrame
            if 'income_statement' in table_name:
                self.income_statement = pd.read_sql_query(query, self.db)
            elif 'balance_sheet' in table_name:
                self.balance_sheet = pd.read_sql_query(query, self.db)
            elif 'cash_flow' in table_name:
                self.cash_flow = pd.read_sql_query(query, self.db)

            # 其他估值数据
        
        header = self.cash_flow.loc[0][0]
        if ('Cash Flow from Operating Activities, Indirect' == header):
            self.operating_cash_flow = self.cash_flow.loc[0][1:-2]
        else:
            raise ValueError("Operating cash flow is not found")

        header = self.balance_sheet.loc[46][0]
        if ('    Total Current Liabilities' == header):
            self.current_liabilities = self.balance_sheet.loc[0][1:-1]
        else:
            raise ValueError("Current liabilities is not found")

    def cash_flow_ratio(self):
        '''
        现金流动负债比率
        Cash Flow Ratio = Operating Cash Flow / Current Liabilities

        Args: None
        Returns:
        '''
        self.cash_flow_ratio = self.operating_cash_flow / self.current_liabilities
        print(self.operating_cash_flow) 
        print(self.current_liabilities)
        print(self.cash_flow_ratio)
        return self.cash_flow_ratio

         

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
    ticker_analysis.cash_flow_ratio()


if __name__ == '__main__':
    main()



