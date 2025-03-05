#!/usr/bin/python3 -u

import msfinance as msf

proxy = 'socks5://127.0.0.1:1088'

stock = msf.Stock(
    debug=True,
    database='sp500.db3',
    proxy=proxy,
)

tickers_list = {
    #'tsla', # Tesla
    #'intc', # Intel
    #'amd', # AMD
    #'googl', # Google
    #'msft', # Microsoft
    #'amzn', # Amazon
    #'nvda', # Nvidia
    #'nflx', # Netflix
    'mnst', # Monster Beverage
    'sbux', # Starbucks
}

# XNAS
for ticker in sorted(tickers_list):
    key_metrics = stock.get_key_metrics(ticker, 'xnas', update=True)
    financials = stock.get_financials(ticker, 'xnas', update=True)

    print(f"Ticker: {ticker}")
    for key_metric in key_metrics:
        print(key_metric)
    for financial in financials:
        print(financial)

tickers_list = {
    'ko', # Coca-Cola
}

# XNYS
for ticker in sorted(tickers_list):
    key_metrics = stock.get_key_metrics(ticker, 'xnys', update=True)
    financials = stock.get_financials(ticker, 'xnys', update=True)

    print(f"Ticker: {ticker}")
    for key_metric in key_metrics:
        print(key_metric)
    for financial in financials:
        print(financial)
