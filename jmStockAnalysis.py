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

        # Assign to zero if item not found in balance sheet
        if not hasattr(self, 'total_long_term_investments'):
            self.total_long_term_investments = \
                pd.Series(0, index=self.balance_sheet.loc[0][1:-1].index)

        if not hasattr(self, 'inventories'):
                self.inventories = pd.Series(0, index=self.balance_sheet.loc[0][1:-1].index)
                self.inventories_increase = self.inventories[-1] - self.inventories[-5]

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
            elif ('        Cash Dividends and Interest Paid' in header): # Dividends paid case 1
                self.dividends_paid = self.cash_flow.loc[i][1:-2]
            elif ('        Cash Dividends Paid to Non-Controlling/Minority Interests' in header): # Dividends paid case 2
                self.dividends_paid = self.cash_flow.loc[i][1:-2]
        
        ## Assign to zeros if item is not found in cash flow 
        if not hasattr(self, 'dividends_paid'):
            self.dividends_paid = pd.Series(0, index=self.cash_flow.loc[0][1:-2].index)

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
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.asset_turnover = self.to_float64(s)
            elif ('Gross Margin %' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.gross_margin = self.to_float64(s)
            elif ('Operating Margin %' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.operating_margin = self.to_float64(s)
            elif ('Net Margin %' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.net_margin = self.to_float64(s)
            elif ('Return on Equity %' in header):
                s = self.operating_and_efficiency.loc[i][1:-3]
                self.return_on_equity = self.to_float64(s)

        # Financial Health
        for i in range(self.financial_health.shape[0]):
            header = self.financial_health.loc[i][0]
            if ('Current Ratio' in header):
                s = self.financial_health.loc[i][1:-2]
                self.current_ratio  = self.to_float64(s)
                # Trim month in index, 'YYYY-MM' 
                self.current_ratio.index = self.current_ratio.index.str.replace(r'-..', '', regex=True)
            elif ('Quick Ratio' in header):
                s = self.financial_health.loc[i][1:-2]
                self.quick_ratio = self.to_float64(s)
                # Trim month in index, 'YYYY-MM' 
                self.quick_ratio.index = self.quick_ratio.index.str.replace(r'-..', '', regex=True)

        # Initial all ratio
        self.get_cash_flow_ratio()
        self.get_cash_flow_adequancy_ratio()
        self.get_cash_reinvestment_ratio()
        self.get_cash_to_total_assets_ratio()
        self.get_days_sales_outstanding()
        self.get_days_inventory_outstanding()
        self.get_days_payables_outstanding()
        self.get_cash_conversion_cycle()
        self.get_operating_cycle()
        self.get_asset_turnover()
        self.get_gross_margin()
        self.get_operating_margin()
        self.get_operation_safety_margin()
        self.get_net_margin()
        self.get_eps()
        self.get_roe()
        self.get_debt_ratio()
        self.get_fixed_assets_to_long_term_liabilities_ratio()
        self.get_current_ratio()
        self.get_quick_ratio()
    
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
        cash_flow_adequancy_ratio \
            = self.operating_cash_flow[-5:].sum() \
                / (-self.capital_expenditures[-5:].sum() + self.inventories_increase - self.dividends_paid[-5:].sum())

        self.cash_flow_adequancy_ratio = pd.Series(index=self.operating_cash_flow.index) 
        self.cash_flow_adequancy_ratio[-1] = cash_flow_adequancy_ratio
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
        平均销货天数，直接从财务数据中获取
        '''
        return self.days_inventory_outstanding

    def get_days_payables_outstanding(self):
        '''
        应付账款天数，直接从财务数据中获取
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
        return self.fixed_assets_to_long_term_liabilities_ratio

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

    def generate_report(self):
        '''
        生成财务分析报告

        Args: None
        Returns:
            Analysis report, pandas.DataFrame
        '''
        self.report = pd.DataFrame()
        self.report = pd.concat([self.report, self.cash_flow_ratio.rename('现金流动负债比率')], axis=1)
        self.report = pd.concat([self.report, self.cash_flow_adequancy_ratio.rename('现金流量允当比率')], axis=1)
        self.report = pd.concat([self.report, self.cash_reinvestment_ratio.rename('现金再投资比率')], axis=1)
        self.report = pd.concat([self.report, self.cash_to_total_assets_ratio.rename('现金占总资产比率')], axis=1) 
        self.report = pd.concat([self.report, self.days_sales_outstanding.rename('平均收现天数')], axis=1)
        self.report = pd.concat([self.report, self.days_inventory_outstanding.rename('平均销货天数')], axis=1) 
        self.report = pd.concat([self.report, self.days_payables_outstanding.rename('应付账款天数')], axis=1)
        self.report = pd.concat([self.report, self.cash_conversion_cycle.rename('现金转换周期')], axis=1)
        self.report = pd.concat([self.report, self.operating_cycle.rename('生意完整周期')], axis=1)
        self.report = pd.concat([self.report, self.asset_turnover.rename('资产周转率')], axis=1)
        self.report = pd.concat([self.report, self.gross_margin.rename('营业毛利率')], axis=1)
        self.report = pd.concat([self.report, self.operating_margin.rename('营业利润率')], axis=1)
        self.report = pd.concat([self.report, self.operation_safety_margin.rename('营业安全边际率')], axis=1)
        self.report = pd.concat([self.report, self.net_margin.rename('净利率')], axis=1)
        self.report = pd.concat([self.report, self.basic_eps.rename('每股收益')], axis=1)
        self.report = pd.concat([self.report, self.return_on_equity.rename('股本回报率')], axis=1)
        self.report = pd.concat([self.report, self.debt_ratio.rename('资产负债率')], axis=1)
        self.report = pd.concat([self.report, self.fixed_assets_to_long_term_liabilities_ratio.rename('长期资产合适率')], axis=1)
        self.report = pd.concat([self.report, self.current_ratio.rename('流动比率')], axis=1)
        self.report = pd.concat([self.report, self.quick_ratio.rename('速动比率')], axis=1) 

        self.report = self.report.sort_index()

        # Turn to a row base table for manual review
        self.report = self.report.transpose()
        return self.report

class CheckRules():
    '''
    对单一股票的数据进行合规分析，高亮有问题的数据
    '''
    def __init__(self, report):
        self.report = report
        self.rules = [
            self.rule_a1, self.rule_a2, self.rule_a3, self.rule_a4, self.rule_a5,
            self.rule_b1, self.rule_b2, self.rule_b3,
            self.rule_c1,
            self.rule_d1, self.rule_d2,
            self.rule_e1, self.rule_e2,
        ]

        self.style_normal  = 'background-color: #e8f5e9; color: #388e3c'
        self.style_warning = 'background-color: #fff9c4; color: #ef6c00'
        self.style_failure = 'background-color: #ffcdd2; color: #c62828'

    def rule_a1(self, row):
        '''
        R.A1 [MUST] 现金流动负债比率 > 100%
        '''
        styles = []
        if row.name == '现金流动负债比率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 1.0: # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_a2(self, row):
        '''
        R.A2 [MUST] 现金流量允当比率 > 100%
        '''
        styles = []
        if row.name == '现金流量允当比率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 1.0: # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles
    
    def rule_a3(self, row):
        '''
        R.A3 [MUST] 现金再投资比率 > 10%
        '''
        styles = []
        if row.name == '现金再投资比率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 0.1: # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_a4(self, row):
        '''
        R.A4 [MUST] 现金占总资产比率 10~25%
        '''
        styles = []
        if row.name == '现金占总资产比率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 0.1 and val < 0.25: # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_a5(self, row):
        '''
        R.A5 [MUST] 平均收现天数，没有增加的趋势
        '''
        styles = []
        if row.name == '平均收现天数':
            # Fit with y = k*x + b
            index = [float(i) for i in row.index.tolist()]
            values = [float(i) for i in row.values]
            k, b = np.polyfit(index, values, 1)
            if k > 0.2:
                styles = [self.style_warning] * len(row)
            else:
                styles = [self.style_normal] * len(row)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_b1(self, row):
        '''
        R.B1 [NTH] 资产周转率 > 1
        '''
        styles = []
        if row.name == '资产周转率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 1 : # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles
    
    def rule_b2(self, row):
        '''
        R.B2 [MUST] 平均销货天数，没有增加的趋势  
        '''
        styles = []
        if row.name == '平均销货天数':
            # Fit with y = k*x + b
            index = [float(i) for i in row.index.tolist()]
            values = [float(i) for i in row.values]
            k, b = np.polyfit(index, values, 1)
            if k > 0.2:
                styles = [self.style_warning] * len(row)
            else:
                styles = [self.style_normal] * len(row)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles
    
    def rule_b3(self, row):
        '''
        R.B3 [MUST] 生意完整周期，没有增加的趋势
        '''
        styles = []
        if row.name == '生意完整周期':
            # Fit with y = k*x + b
            index = [float(i) for i in row.index.tolist()]
            values = [float(i) for i in row.values]
            k, b = np.polyfit(index, values, 1)
            if k > 0.2:
                styles = [self.style_warning] * len(row)
            else:
                styles = [self.style_normal] * len(row)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles
    
    def rule_c1(self, row):
        '''
        R.C1 [MUST] 营业毛利率 > 30%
        '''
        styles = []
        if row.name == '营业毛利率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 30 : # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_d1(self, row):
        '''
        R.D1 [MUST] 资产负债率 < 60%
        '''
        styles = []
        if row.name == '资产负债率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val < 0.6 : # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles
    
    def rule_d2(self, row):
        '''
        R.D2 [MUST] 长期资产合适率 > 150%
        '''
        styles = []
        if row.name == '长期资产合适率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 1.5 : # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_e1(self, row):
        '''
        R.E1 [MUST] 流动比率 > 300%
        '''
        styles = []
        if row.name == '流动比率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 3.0 : # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles

    def rule_e2(self, row):
        '''
        R.E2 [MUST] 速动比率 > 150%
        '''
        styles = []
        if row.name == '速动比率':
            for col, val in row.items():
                if pd.isnull(val):
                    styles.append('')
                elif val > 1.5 : # Pass case
                    styles.append(self.style_normal)
                else: # Fail case
                    styles.append(self.style_failure)
        else:
            styles = [''] * len(row)

        assert len(styles) == len(row), "Styles length error"
        return styles
    
    def check_all(self):
        '''
        应用所有分析规则

        Args: None
        Returns:
            Report with abnormal data highlight, pandas.DataFrame.style
        '''
        styler = self.report.style
        for func in self.rules:
            styler = styler.apply(func, axis=1)

        return styler

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

# Unit Test Case
#    print("cash_flow_ratio:\n",             ticker_analysis.get_cash_flow_ratio())
#    print("cash_flow_adequancy_ratio:\n",   ticker_analysis.get_cash_flow_adequancy_ratio())
#    print("cash_reinvestment_ratio:\n",     ticker_analysis.get_cash_reinvestment_ratio())
#    print("cash_to_total_assets_ratio:\n",  ticker_analysis.get_cash_to_total_assets_ratio())
#    print("days_sales_outstanding:\n",      ticker_analysis.get_days_sales_outstanding())
#    print("days_inventory_outstanding:\n",  ticker_analysis.get_days_inventory_outstanding())
#    print("days_payables_outstanding:\n",   ticker_analysis.get_days_payables_outstanding())
#    print("cash_conversion_cycle:\n",       ticker_analysis.get_cash_conversion_cycle())
#    print("operating_cycle:\n",             ticker_analysis.get_operating_cycle())
#    print("asset_turnover:\n",              ticker_analysis.get_asset_turnover())
#    print("gross_margin:\n",                ticker_analysis.get_gross_margin())
#    print("operating_margin:\n",            ticker_analysis.get_operating_margin())
#    print("operation_safety_margin:\n",     ticker_analysis.get_operation_safety_margin())
#    print("net_margin:\n",                  ticker_analysis.get_net_margin())
#    print("eps:\n",                         ticker_analysis.get_eps())
#    print("roe:\n",                         ticker_analysis.get_roe())
#    print("debt_ratio:\n",                  ticker_analysis.get_debt_ratio())
#    print("long_term_ratio:\n",             ticker_analysis.get_fixed_assets_to_long_term_liabilities_ratio())
#    print("current_ratio:\n",               ticker_analysis.get_current_ratio())
#    print("quick_ratio:\n",                 ticker_analysis.get_quick_ratio())
#    print("Report:\n",                      ticker_analysis.generate_report())

    origin_report = ticker_analysis.generate_report()
    report = CheckRules(origin_report)
    checked_report = report.check_all()


    # Output style control
    ## Format and keep 2 decimal places, NaN to '-'
    checked_report = checked_report.format("{:.2f}", na_rep='-')

    ## Set table style
    table_styles = [
        dict(selector="table", props=[("width", "100%")]),
        
        dict(selector="th", props=[
            ("font-size", "100%"),
            ("text-align", "center"),
            ("font-weight", "bold"),
        ]),

        # 1st col header with 20%
        dict(selector="th:nth-child(1)", props=[("width", "20%")]),
        
        # other header with 20%
        dict(selector="th:not(:first-child)", props=[("width", "8%")]), 
        
        dict(selector="td", props=[("text-align", "center")]),
        #dict(selector="table, th, td", props=[("border", "1px solid black")]),
        # Set caption
        dict(selector="caption", props=[
            ("caption-side", "top"),
            ("font-size", "150%"),
            ("font-weight", "bold"),
            ("text-align", "center"),  
            ("margin", "20px 0 20px 0")
        ])
    ]
    checked_report = checked_report.set_table_styles(table_styles, overwrite=False)
    checked_report = checked_report.set_caption(opts.ticker)
    
    # Render to html 
    html = checked_report.to_html()
    print(html)

if __name__ == '__main__':
    main()



