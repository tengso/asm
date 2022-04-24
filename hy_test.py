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


def get_bbg_port():
    prices = pd.read_csv('data/bbg.csv', delimiter='\t')
    prices['Date'] = pd.to_datetime(prices.Date)
    prices = prices.set_index('Date').sort_index()
    prices = prices[~prices.index.duplicated(keep='first')]
    return prices


def get_port():
    prices = pd.read_csv('data/port_backward.csv')
    prices['Date'] = pd.to_datetime(prices.Date)
    prices = prices.set_index('Date').sort_index()
    return prices


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


def compare_price():
    start_date = datetime.date(2019, 1, 1)
    end_date = datetime.date(2022, 4, 1, )
    symbol = 'HK.00316'
    price = util.get_price(symbol, start_date, end_date, adjusted=True)
    price_raw = util.get_price(symbol, start_date, end_date, adjusted=False)
    price.plot(color='blue', alpha=0.5)
    price_raw.plot(color='red', alpha=0.5)
    plt.show()

    corp_action = util.get_corp_action(symbol)
    corp_action['ex_div_date'] = pd.to_datetime(corp_action['ex_div_date'])
    corp_action = corp_action.set_index('ex_div_date').sort_index()
    corp_action['raw_price'] = price_raw
    corp_action['price'] = price

    corp_action['my_price'] = corp_action.backward_adj_factorA * corp_action.raw_price + corp_action.backward_adj_factorB
    corp_action['2019'][['my_price', 'price', 'raw_price']]
    corp_action[['my_price', 'price', 'raw_price']].tail()
    corp_action['2019-01'].head()


def download_corp_actions(symbols):
    data = {}
    for symbol in symbols:
        print(symbol)
        d = util.get_corp_action(symbol)
        data[symbol] = d
        time.sleep(1)
    return data


def compute_cash_div_yield(symbol, corp_action):
    symbol = 'HK.00316'

    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2022, 4, 1, )

    ca = util.get_corp_action(symbol)
    # ca['2021']
    raw_price = util.get_price(symbol, start_date, end_date, adjusted=False)

    year_end_prices = {}
    for year in range(raw_price.index.min().year, raw_price.index.max().year, 1):
        year_end_prices[year] = raw_price[str(year)].tail(1).iloc[0]

        # year_end_prices.append(raw_price[str(year)].tail(1))
    year_end_prices = pd.Series(year_end_prices)
    # year_end_prices['year'] = [date.year for date in year_end_prices.index]
    # year_end_prices.head()

    ca['price'] = raw_price
    ca = ca.fillna(0)
    # ca['div_yield'] = ca.per_cash_div / ca.price
    ca['year'] = [date.year for date in ca.index]
    # ca['annual_cash_div'] =
    # ca['2018':][['per_cash_div', 'per_share_div_ratio', 'price', 'div_yield']]

    yearly_cash_div = ca.groupby('year').per_cash_div.sum()
    data = pd.DataFrame(dict(yearly_cash_div=yearly_cash_div, ye_price=year_end_prices))
    data['annual_cash_div_yield'] = data.yearly_cash_div / data.ye_price

    return data
    # data.yearly_cash_div_yield.plot(kind='bar')
    # data.yearly_div.plot(kind='bar')
    # plt.show()

    # ca['2021']

# ch_stocks = [s for s in stocks if 'HK' not in s]
# hk_stocks
# ch_stocks

start_date = datetime.date(2019, 1, 1)
end_date = datetime.date(2022, 4, 1, )


port = get_port()
port_size = len(port.columns)

hk_stocks = [s for s in port.columns if 'HK' in s]
corp_action = download_corp_actions(hk_stocks)
corp_action.keys()

corp_action['HK.00316']
bbg_port['HK.00316']

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

t = yf.Ticker('0665.HK')
t.dividends
t.info
port = get_port()
port.columns

bbg_port = get_bbg_port()
stocks = [format_bbg_symbol(stock) for stock in bbg_port.columns]
tickers = [yf.Ticker(stock, session=session) for stock in stocks]

for ticker in tickers:
    print(ticker.info['longName'])

tickers[1].news


def compute_roe(ticker):
    earnings = ticker.earnings.Earnings
    equity = ticker.balancesheet.loc['Total Stockholder Equity']
    equity.index = pd.to_datetime(equity.index)
    equity = equity.sort_index()
    equity.index = [d.year for d in equity.index.to_list()]
    return earnings / equity


ticker = tickers[2]
ticker.info['longName']
compute_roe(ticker)
# check roe
# check dividend yield vol
ticker.stats()

ticker.calendar
h = ticker.history(start=datetime.date(2000, 1, 1), end=datetime.date.today())
h[h.Dividends > 0]













