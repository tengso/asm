import pyfolio as pf
import datetime
import time
import pandas as pd
import util
import matplotlib.pyplot as plt
import futu
import yfinance as yf
import requests_cache

session = requests_cache.CachedSession('yfinance.cache')


def get_bbg_port():
    prices = pd.read_csv('data/bbg.csv', delimiter='\t')
    prices['Date'] = pd.to_datetime(prices.Date)
    prices = prices.set_index('Date').sort_index()
    return prices


def get_port():
    prices = pd.read_csv('data/port_backward.csv')
    prices['Date'] = pd.to_datetime(prices.Date)
    prices = prices.set_index('Date').sort_index()
    return prices


def is_valid_equity_ticker(ticker):
    return ticker.info['regularMarketPrice'] is not None and ticker.info['quoteType'] == 'EQUITY'


def format_symbol(code):
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
        return tokens[1] + '.' + tokens[0].zfill(5)


def download_prices(is_save_csv=False):
    start_date = datetime.date(2018, 1, 1)
    end_date = datetime.date(2022, 4, 1)

    bbg_port = get_bbg_port()
    bbg_port.columns = [format_symbol(col) for col in bbg_port.columns]

    stocks = bbg_port.columns
    # hk_stocks = [s for s in stocks if 'HK' in s]
    # ch_stocks = [s for s in stocks if 'HK' not in s]
    prices = dict()
    for stock in stocks:
        price = util.get_price(stock, start_date, end_date, adjusted=True)
        print(stock, len(price))
        prices[stock] = price
        time.sleep(1)

    all_prices = pd.DataFrame(prices)

    if is_save_csv:
        p = '/Users/song/projects/PycharmProjects/asm/data/port_backward.csv'
        all_prices.to_csv(p, index_label='Date')

    return all_prices


# hk_stocks
# ch_stocks

start_date = datetime.date(2019, 1, 1)
end_date = datetime.date(2022, 4, 1, )


port = get_port()
port_size = len(port.columns)

bbg_port = get_bbg_port()
bbg_port.columns = port.columns
bbg_port_size = len(bbg_port.columns)

p = '/Users/song/projects/PycharmProjects/asm/data/bbg_return.csv'
bbg_ret = pd.read_csv(p, delimiter='\t')
bbg_ret['Date'] = pd.to_datetime(bbg_ret.Date)
bbg_ret = bbg_ret.set_index('Date').sort_index()
bbg_ret.columns = [format_symbol(col) for col in bbg_ret.columns]
len(bbg_ret.columns)
bbg_ret.head()


# port = port.dropna()
port = port.pct_change()
port = (port / port_size).sum(axis=1)
port['2019':].cumsum().plot()
plt.show()
port['2017']

port.columns

symbol = 'HK.00316'
price_raw = util.get_price(symbol, start_date, end_date, adjusted=False)
price_adjusted = util.get_price(symbol, start_date, end_date, adjusted=True)
bbg_raw = bbg_port[symbol]


compare = pd.DataFrame(dict(raw=price_raw, adjusted=price_adjusted, bbg_raw=bbg_raw))
compare[['raw', 'bbg_raw']].plot(alpha=0.5, title=symbol)
compare.plot(alpha=0.5, title=symbol)
plt.show()


price_adjusted.pct_change().cumsum().plot(color='red')
bbg_ret[symbol]['2019':].cumsum().plot(color='blue')
plt.show()


# bbg_port = bbg_port.dropna()
bbg_port = bbg_port.pct_change()
bbg_port = (bbg_port / bbg_port_size).sum(axis=1)
bbg_port['2019':].cumsum().plot()
plt.show()

bbg_port['2019']['HK.00316'].pct_change().cumsum().plot()
port['2019']['HK.00316'].pct_change().cumsum().plot()
plt.show()

hsi = util.get_price('HK.02800', start_date, end_date, adjusted=True)
hsi = hsi.pct_change()

hscei = util.get_price('HK.02828', start_date, end_date, adjusted=True)
hscei = hscei.pct_change()

hy_etf = util.get_price('HK.03110', start_date, end_date, adjusted=True)
hy_etf = hy_etf.pct_change()

stocks[8]

price = yf.download(stocks[8], start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
len(price)


len(prices)

all_prices = all_prices.dropna()
all_prices = all_prices.pct_change()

port = (all_prices / 45).sum(axis=1)
len(port)

futu.ge
hy_etf.cumsum().plot()
plt.show()

port_ls = port - hsi

port.cumsum().plot()
port_ls.cumsum().plot()
plt.show()


hscei.cumsum().plot()
plt.show()

pf.ep.annual_return(port_ls)
pf.ep.annual_return(port)

pf.ep.sharpe_ratio(port_ls)
pf.ep.sharpe_ratio(port)

port.std() * 16
hsi.std() * 16


port.cumsum().plot()
plt.show()

len(all_prices.columns)
all_prices = all_prices.dropna()
len(all_prices)
all_prices['ret'] = all_prices.sum(axis=1) / 20
# all_prices.ret

col = [c for c in all_prices.columns if c != 'ret']
all_prices[col].cumsum().plot()

all_prices.ret.cumsum().plot()
# plt.show()

all_prices['HK.01088'].cumsum().plot()

pf.ep.sharpe_ratio(all_prices.ret)

max_drawdown = pf.ep.max_drawdown(all_prices.ret)
annual_return = pf.ep.annual_return(all_prices.ret)
annual_vol = pf.ep.annual_volatility(all_prices.ret)

perf = pd.DataFrame([dict(start_date=start_date, end_date=end_date, annual_return=annual_return, annual_vol=annual_vol, max_drawdown=max_drawdown)])





corp_316 = util.get_corp_action('HK.00316')
corp_316


compare = pd.DataFrame(dict(bbg=bbg_port['2019':], port=port['2019':]))
compare.cumsum().plot()
plt.show()


port.columns
# bbg_prices.head()
# len(bbg_prices.columns)

