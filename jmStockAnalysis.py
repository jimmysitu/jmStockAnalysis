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
            elif '_growth' in table_name:
                self.growth = pd.read_sql_query(query, self.db)
            elif '_financial_health' in table_name:
                self.financial_health = pd.read_sql_query(query, self.db)
            elif '_operating_and_efficiency' in table_name:
                self.operating_and_efficiency = pd.read_sql_query(query, self.db)

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

        # Operating and efficiency
        for i in range(self.operating_and_efficiency.shape[0]):
            header = self.operating_and_efficiency.loc[i][0]
            if ('Days Sales Outstanding' in header):
                self.days_sales_outstanding = self.operating_and_efficiency.loc[i][1:-3]
            elif ('Days Inventory' in header):
                self.days_inventory_outstanding = self.operating_and_efficiency.loc[i][1:-3]
            elif ('Payables Period' in header):
                self.days_payables_outstanding = self.operating_and_efficiency.loc[i][1:-3]


    def get_cash_flow_ratio(self):
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

         

    def get_cash_flow_adequancy_ratio(self):
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

    def get_cash_reinvestment_ratio(self):
        '''
        现金再投资比率
        Cash Re-investment Ratio =
            (Operating Cash Flow - Dividends Paid) / (Total Assets - Current Liabilites)
        '''
        self.cash_reinvestment_ratio \
            = (self.operating_cash_flow + self.dividends_paid) \
                / (self.total_assets - self.current_liabilities)

        return self.cash_reinvestment_ratio     

    def get_cash_to_total_assets_ratio(self):
        '''
        现金与约当现金比率
        Cash to Total Assets Ratio =
            Cash and Cash Equivalents / Total Assets
        '''
        self.cash_to_total_assets_ratio \
            = self.cash_and_cash_equivalents / self.total_assets

        return self.cash_to_total_assets_ratio
    
    def get_days_sales_outstanding(self):
        '''
        平均收现天数，直接从财务数据中获取
        Days Sales Outstanding = 365 / Receivables Turnover
        '''
        return self.days_sales_outstanding

    def get_days_inventory_outstanding(self):
        '''
        平均销货日数，直接从财务数据中获取
        '''
        return self.days_inventory_outstanding

    def get_days_payables_outstanding(self):
        '''
        应付账款日数，直接从财务数据中获取
        '''
        return self.days_payables_outstanding

    def get_cash_conversion_cycle(self):
        '''
        现金转换周期
        Cash Coversion Cycle = \
            Days Inventory Outstanding (DIO) + Days Sales Outstanding (DSO) − Days Payables Outstanding (DPO)
        '''
        self.cash_conversion_cycle = \
            self.days_inventory_outstanding + self.days_sales_outstanding - self.days_payables_outstanding
        return self.cash_conversion_cycle
            
    def get_operating_cycle(self):
        '''
        生意完整周期
        Operating Cycle = DIO + DSO
        '''
        self.operating_cycle = self.days_inventory_outstanding + self.days_sales_outstanding
        return self.operating_cycle

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
    print("cash_flow_ratio:\n",             ticker_analysis.get_cash_flow_ratio())
    print("cash_flow_adequancy_ratio:\n",   ticker_analysis.get_cash_flow_adequancy_ratio())
    print("cash_reinvestment_ratio:\n",     ticker_analysis.get_cash_reinvestment_ratio())
    print("cash_to_total_assets_ratio:\n",  ticker_analysis.get_cash_to_total_assets_ratio())
    print("days_sales_outstanding:\n",      ticker_analysis.get_days_sales_outstanding())
    print("days_inventory_outstanding:\n",  ticker_analysis.get_days_inventory_outstanding())
    print("days_payables_outstanding:\n",   ticker_analysis.get_days_payables_outstanding())
    print("cash_conversion_cycle:\n",       ticker_analysis.get_cash_conversion_cycle())
    print("operating_cycle:\n",             ticker_analysis.get_operating_cycle())


if __name__ == '__main__':
    main()



