import os
import datetime

import yfinance as yf
import pandas as pd

from futu import SysConfig
from futu import OpenQuoteContext, KLType, AuType, TradeDateMarket, RET_OK
from futu import AuType


# '/Users/song/PycharmProjectsSandbox/happyvalley/futu')

default_key_path = os.environ.get('FUTUD_KEY_PATH', None)
default_host = os.environ.get('FUTUD_HOST', '127.0.0.1')
default_port = os.environ.get('FUTUD_PORT', 11111)
default_trading_password = os.environ.get('FUTU_TRADING_PASSWORD', '721117')


class FutuConfig:
    def __init__(self, host=None, port=None, key_path=None, trading_password=None, is_encrypt=True):
        self.host = default_host if host is None else host
        self.port = default_port if port is None else port
        self.key_path = default_key_path if key_path is None else key_path
        self.trading_password = default_trading_password if trading_password is None else trading_password
        self.is_encrypt = is_encrypt

        if self.key_path:
            SysConfig.set_init_rsa_file(self.key_path)

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_trading_password(self):
        return self.trading_password

    # def is_encrypt(self):
    #     return self.is_encrypt


def get_corp_action(symbol):
    config = FutuConfig()
    context = OpenQuoteContext(host=config.get_host(), port=config.get_port())
    ret, data = context.get_rehab(symbol)
    context.close()
    return data


def get_kline(symbol, start_date, end_date, ktype=KLType.K_DAY, autype=AuType.NONE, max_count=None):
    config = FutuConfig()
    context = OpenQuoteContext(host=config.get_host(), port=config.get_port())
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    ret, data, _ = context.request_history_kline(symbol, start=start_date, end=end_date, ktype=ktype,
                                                 autype=autype, max_count=max_count)
    context.close()
    if isinstance(data, pd.DataFrame):
        return data
    else:
        raise Exception(f'failed to get kline for {symbol} from {start_date} to {end_date}: {data}')


def get_price(symbol, start_date, end_date, adjusted=True):
    if symbol.startswith('HK.'):
        prices = get_kline(symbol, start_date, end_date, autype=AuType.QFQ if adjusted else AuType.NONE)
        prices['date'] = pd.to_datetime(prices.time_key)
        prices = prices.set_index('date').sort_index()
        prices = prices.close
        return prices
    else:
        # make sure to use yahoo symbol
        price = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        return price['Adj Close'] if adjusted else price['Close']


# symbol = 'HK.00665'
# start_date = datetime.date(2013, 1, 1)
# end_date = datetime.date(2022, 2, 2)
#
# prices = get_price(symbol, start_date, end_date, adjusted=False)
# prices.head(), prices.tail()


