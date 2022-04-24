import util
import pyfolio as pf
import datetime
import time
import pandas as pd
import util
import matplotlib.pyplot as plt
import futu
import yfinance as yf
import requests_cache
import time

session = requests_cache.CachedSession('yfinance.cache')


def is_valid_equity_ticker(ticker):
    return ticker.info['regularMarketPrice'] is not None and ticker.info['quoteType'] == 'EQUITY'


def format_bbg_symbol(code, is_futu=False):
    tokens = code.split(' ')
    market = tokens[1]
    code = tokens[0]
    print(f'format {code}')
    if market != 'HK':
        for market in ['SS', 'SZ']:
            symbol = f'{code}.{market}'
            ticker = yf.Ticker(symbol, session=session)
            if is_valid_equity_ticker(ticker):
                return symbol
        else:
            raise RuntimeError(f'invalid {code}')
    else:
        if is_futu:
            return market + '.' + tokens[0].zfill(5)
        else:
            return tokens[0].zfill(4) + '.' + market


def get_bbg_port():
    prices = pd.read_csv('data/bbg.csv', delimiter='\t')
    prices['Date'] = pd.to_datetime(prices.Date)
    prices = prices.set_index('Date').sort_index()
    prices = prices[~prices.index.duplicated(keep='first')]
    return prices


def compute_roe(ticker):
    # ticker = yf.Ticker('601988.SS')

    earnings = ticker.earnings.Earnings
    earnings = earnings[~earnings.index.duplicated(keep='last')]

    equity = ticker.balancesheet.loc['Total Stockholder Equity']
    equity.index = pd.to_datetime(equity.index)
    equity = equity.sort_index()
    equity.index = [d.year for d in equity.index.to_list()]
    equity = equity[~equity.index.duplicated(keep='last')]

    return earnings / equity


port = get_bbg_port()
stocks = [format_bbg_symbol(stock) for stock in port.columns]

stock_data = {}
for stock in stocks:
    ticker = yf.Ticker(stock, session=session)
    stock_data[stock] = ticker
    print(ticker.info['longName'])

roe_data = {}
for stock in stocks:
    roe = compute_roe(stock_data[stock])
    roe_data[stock] = roe

roe_data = pd.DataFrame(roe_data)

roe_data.std() > 0.2

stock_data['0316.HK'].info
stock_data['0883.HK'].balancesheet
stock_data['1378.HK'].balancesheet

# historical div yield

div_data = {}
for stock, ticker in stock_data.items():
    div_data[stock] = ticker.info['fiveYearAvgDividendYield']

div_data = pd.Series(div_data)
div_data.sort_values()

