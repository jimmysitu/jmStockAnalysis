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
        # Income statement
        for i in range(self.income_statement.shape[0]):
            header = self.income_statement.loc[i][0]
            if ('Basic EPS' in header):
                self.basic_eps = self.income_statement.loc[i][1:-2].replace('-', 0)

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
            elif ('Total Liabilities' in header):
                self.total_liabilities = self.balance_sheet.loc[i][1:-1]
            elif ('Total Equity' in header):
                self.total_equity = self.balance_sheet.loc[i][1:-1]
            elif ('    Total Non-Current Liabilities' in header):
                self.total_noncurrent_liabilities = self.balance_sheet.loc[i][1:-1]
            elif ('    Total Non-Current Assets' in header):
                self.total_noncurrent_assets = self.balance_sheet.loc[i][1:-1]
            elif ('        Net Property, Plant and Equipment' in header):
                self.net_ppe = self.balance_sheet.loc[i][1:-1]
            elif ('        Total Long Term Investments' in header):
                self.total_long_term_investments = self.balance_sheet.loc[i][1:-1]

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
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.days_sales_outstanding = self.to_float64(s)
            elif ('Days Inventory' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.days_inventory_outstanding = self.to_float64(s)
            elif ('Payables Period' in header):
                s = self.operating_and_efficiency.loc[i][1:-3].replace('-', 0)
                self.days_payables_outstanding = self.to_float64(s)
            elif ('Asset Turnover' in header):
                self.asset_turnover = self.operating_and_efficiency.loc[i][1:-3]
            elif ('Gross Margin %' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.gross_margin = self.to_float64(s)
            elif ('Operating Margin %' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.operating_margin = self.to_float64(s)
            elif ('Net Margin %' in header):
                s= self.operating_and_efficiency.loc[i][1:-3]
                self.net_margin = self.to_float64(s)
            elif ('Return on Equity %' in header):
                self.return_on_equity = self.operating_and_efficiency.loc[i][1:-3]

        for i in range(self.financial_health.shape[0]):
            header = self.financial_health.loc[i][0]
            if ('Current Ratio' in header):
                self.current_ratio = self.financial_health.loc[i][1:-3]
            elif ('Quick Ratio' in header):
                self.quick_ratio = self.financial_health.loc[i][1:-3]

    def to_float64(self, series):
        series = series.replace('-', 0)
        series = series.astype(np.float64)
        return series

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
        print(self.days_inventory_outstanding)
        print(self.days_sales_outstanding)
        print(self.days_sales_outstanding.apply(type))
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

    def get_asset_turnover(self):
        '''
        资产周转率，直接从财务数据中获取
        '''
        return self.asset_turnover

    def get_gross_margin(self):
        '''
        营业毛利率，直接从财务数据中获取
        '''
        return self.gross_margin
    

    def get_operating_margin(self):
        '''
        营业利润率，直接从财务数据中获取
        '''
        return self.operating_margin
    
    def get_operation_safety_margin(self):
        '''
        营业安全边际率
        Operation Safety Margin = Operating Margin / Gross Margin
        '''
        self.operation_safety_margin = self.operating_margin / self.gross_margin
        return  self.operation_safety_margin

    def get_net_margin(self):
        '''
        净利率，直接从财务数据中获取
        '''
        return self.net_margin
    
    def get_eps(self):
        '''
        每股收益，直接从财务数据中获取
        '''
        return self.basic_eps
    
    def get_roe(self):
        '''
        股本回报率，直接从财务数据中获取
        '''
        return self.return_on_equity
    
    def get_debt_ratio(self):
        '''
        资产负债率
        Debt Ratio = Total Liabilities / Total Assets
        '''
        self.debt_ratio = self.total_liabilities / self.total_assets
        return self.debt_ratio
    
    def get_fixed_assets_to_long_term_liabilities_ratio(self):
        '''
        长期资产合适率 = (所有者权益 + 长期负债) / (固定资产 + 长期投资) 
        '''
        self.fixed_assets_to_long_term_liabilities_ratio = \
            (self.total_equity + self.total_noncurrent_liabilities) / \
            (self.net_ppe + self.total_long_term_investments)

    def get_current_ratio(self):
        '''
        流动比率，直接从财报数据中获取
        '''
        return self.current_ratio

    def get_quick_ratio(self):
        '''
        速动比率，直接从财报数据中获取
        '''
        return self.quick_ratio



def main():
    parser = OptionParser()

    parser.add_option("-t", "--ticker",
                action="store", dest="ticker",
                help="Stock ticker")
    parser.add_option("--db", "--database",
                action="store", dest="database",
                help="Finance database, which is saved by msfinance")

    (opts, args) = parser.parse_args()

    # Temp test code
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
    print("asset_turnover:\n",              ticker_analysis.get_asset_turnover())
    print("gross_margin:\n",                ticker_analysis.get_gross_margin())
    print("operating_margin:\n",            ticker_analysis.get_operating_margin())
    print("operation_safety_margin:\n",     ticker_analysis.get_operation_safety_margin())
    print("net_margin:\n",                  ticker_analysis.get_net_margin())
    print("eps:\n",                         ticker_analysis.get_eps())
    print("roe:\n",                         ticker_analysis.get_roe())
    print("debt_ratio:\n",                  ticker_analysis.get_debt_ratio())
    print("long_term_ratio:\n",             ticker_analysis.get_fixed_assets_to_long_term_liabilities_ratio())
    print("current_ratio:\n",               ticker_analysis.get_current_ratio())
    print("quick_ratio:\n",                 ticker_analysis.get_quick_ratio())



if __name__ == '__main__':
    main()



