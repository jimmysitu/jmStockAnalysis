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
            if ('Total Assets' in header):
                self.total_assets = self.balance_sheet.loc[i][1:-1]
            elif ('    Total Current Liabilities' in header):
                self.current_liabilities = self.balance_sheet.loc[i][1:-1]
            elif ('        Inventories' in header):
                self.inventories = self.balance_sheet.loc[i][1:-1]
                self.inventories_increase = self.inventories[-1] - self.inventories[-5]
            elif ('            Cash and Cash Equivalents' in header):
                self.cash_and_cash_equivalents = self.balance_sheet.loc[i][1:-1]

        # Cash flow 
        for i in range(self.cash_flow.shape[0]):
            header = self.cash_flow.loc[i][0]
            if ('Cash Flow from Operating Activities, Indirect' in header):
                self.operating_cash_flow = self.cash_flow.loc[i][1:-2]
            elif ('Cash Flow from Investing Activities' in header):
                self.investing_cash_flow = self.cash_flow.loc[i][1:-2]
            elif ('        Purchase/Sale and Disposal of Property, Plant and Equipment, Net' in header):
                self.capital_expenditures = self.cash_flow.loc[i][1:-2]
            elif ('                Repayments for Short Term Debt' in header):
                self.st_debt_repayments = self.cash_flow.loc[i][1:-2]
            elif ('                Repayments for Long Term Debt' in header):
                self.lt_debt_repayments = self.cash_flow.loc[i][1:-2]
            elif ('        Cash Dividends and Interest Paid' in header):
                self.dividends_paid = self.cash_flow.loc[i][1:-2]



    def cash_flow_ratio(self):
        '''
        现金流动负债比率
        Cash Flow Ratio = Operating Cash Flow / Current Liabilities

        Args: None
        Returns:
            Cash flow ratio 
        '''
        self.cash_flow_ratio \
            = self.operating_cash_flow / self.current_liabilities
        return self.cash_flow_ratio

         

    def cash_flow_adequancy_ratio(self):
        '''
        现金流量允当比率
        Cash Flow Adequancy Ratio = 
            (5yrs Operating Cash Flow) / 
            (5yrs Captial Expenditures + 5yrs Inventories Increase + 5yrs Dividends Paid)
        '''
        self.cash_flow_adequancy_ratio \
            = self.operating_cash_flow.sum() \
                / (-self.capital_expenditures.sum() + self.inventories_increase - self.dividends_paid.sum())
        
        return self.cash_flow_adequancy_ratio

    def cash_reinvestment_ratio(self):
        '''
        现金再投资比率
        Cash Re-investment Ratio =
            (Operating Cash Flow - Dividends Paid) / (Total Assets - Current Liabilites)
        '''
        self.cash_reinvestment_ratio \
            = (self.operating_cash_flow + self.dividends_paid) \
                / (self.total_assets - self.current_liabilities)

        return self.cash_reinvestment_ratio     

    def cash_to_total_assets_ratio(self):
        '''
        现金与约当现金比率
        Cash to Total Assets Ratio =
            Cash and Cash Equivalents / Total Assets
        '''
        self.cash_to_total_assets_ratio \
            = self.cash_and_cash_equivalents / self.total_assets

        return self.cash_to_total_assets_ratio


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
    print(ticker_analysis.cash_flow_adequancy_ratio())
    print(ticker_analysis.cash_reinvestment_ratio())
    print(ticker_analysis.cash_to_total_assets_ratio())


if __name__ == '__main__':
    main()



