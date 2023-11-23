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

        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{ticker}%'"
        tables = pd.read_sql_query(query, self.db)

        for table_name in tables['name']:
            query = f"SELECT * FROM '{table_name}'"

            # 保存三大财报原始数据，DataFrame
            if 'income_statement_' in table_name:
                self.income_statement = pd.read_sql_query(query, self.db)
            elif 'balance_sheet_' in table_name:
                self.balance_sheet = pd.read_sql_query(query, self.db)
            elif 'cash_flow_' in table_name:
                self.cash_flow = pd.read_sql_query(query, self.db)

            # 其他估值数据

        # 提取财报原始数据
        # Balance sheet 
        for i in range(self.balance_sheet.shape[0]):
            header = self.balance_sheet.loc[i][0]
            if ('Total Current Liabilities' in header):
                self.current_liabilities = self.balance_sheet.loc[i][1:-1]

        # Cash flow 
        for i in range(self.cash_flow.shape[0]):
            header = self.cash_flow.loc[i][0]
            if ('Cash Flow from Operating Activities, Indirect' in header):
                self.operating_cash_flow = self.cash_flow.loc[i][1:-2]


    def cash_flow_ratio(self):
        '''
        现金流动负债比率
        Cash Flow Ratio = Operating Cash Flow / Current Liabilities

        Args: None
        Returns:
            Cash flow ratio 
        '''
        self.cash_flow_ratio = self.operating_cash_flow / self.current_liabilities
        return self.cash_flow_ratio

         

    def cash_flow_adequancy_ratio(self, ticker):
        '''
        现金流量允当比率
        Cash Flow Adequancy Ratio = 
            (5yrs Operating Cash Flow) / (5yrs Captial Expenditures + 5yrs Debt Repayments + 5yrs Dividends Paid)
        '''
        pass

    def cash_reinvestment_ratio(self, ticker):
        '''
        现金再投资比率
        Cash Re-investment Ratio =
            (Operationg Cash Flow - Dividends Paid) / ()
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
    print(ticker_analysis.cash_flow_ratio())


if __name__ == '__main__':
    main()



