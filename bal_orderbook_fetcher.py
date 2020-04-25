import requests
import pandas as pd
from datetime import datetime
import ccxt
import sqlite3
import config

ex = 'indodax'
currency_f = 'idr'
currency_c = 'eth'
pair = currency_c.upper() + '/' + currency_f.upper()
now = datetime.utcnow()
now_ts = now.timestamp()

arg = {
    'apiKey': config.indodax['apiKey'],
    'secret': config.indodax['secret']
}

params = {
    'pair': 'eth_idr',
    'count': 50,  # number of trades return
    'end': now_ts
}


def get_fx(currency_f):
    fx = requests.get(
        'https://apilayer.net/api/live?access_key=a1d6d82a3df7cf7882c9dd2b35146d6e&source=USD&format=1').json()
    return fx['quotes']['USD' + currency_f.upper()]


def get_basic(time):
    now_ts = datetime.timestamp(time)
    fx_name = 'USD/' + currency_f.upper()
    fx_rate = get_fx(currency_f)
    basics = {'time': now.strftime("%y-%m-%d %H:%M:%S"),
              'utc': [now_ts],
              'exchange': [ex],
              'pair': [pair],
              fx_name: [float(fx_rate)]}
    basics = pd.DataFrame(basics)
    return basics


def get_ob(ex, pair):
    ex_instance = eval('ccxt.' + ex)()
    ob = ex_instance.fetch_order_book(pair)
    bid_px = dict(zip([str(i) + '_bid_px' for i in range(1, 6)],
                      [float(ob['bids'][i][0]) for i in range(5)]))
    ask_px = dict(zip([str(i) + '_ask_px' for i in range(1, 6)],
                      [float(ob['asks'][i][0]) for i in range(5)]))
    bid_sz = dict(zip([str(i) + '_bid_sz' for i in range(1, 6)],
                      [float(ob['bids'][i][1]) for i in range(5)]))
    ask_sz = dict(zip([str(i) + '_ask_sz' for i in range(1, 6)],
                      [float(ob['asks'][i][1]) for i in range(5)]))
    elements = {}
    elements.update(bid_px)
    elements.update(ask_px)
    elements.update(bid_sz)
    elements.update(ask_sz)
    df = pd.DataFrame({k: [v] for k, v in elements.items()})
    return df


def get_td(ex):
    ex_instance = eval('ccxt.' + ex)(arg)
    trades = ex_instance.privatePostTradeHistory(params)['return']['trades']
    df = pd.DataFrame(trades)
    df['time'] = df['trade_time'].apply(
        lambda x: datetime.fromtimestamp(int(x)))
    df = df.rename(columns={'trade_time': 'utc'})
    return df


def get_bal(ex, currency_f):
    ex_instance = eval('ccxt.' + ex)(arg)
    bal = ex_instance.fetch_balance()
    bal_fiat_free = bal[currency_f.upper()]['free']
    bal_eth_free = bal['ETH']['free']
    bal_fiat_used = bal[currency_f.upper()]['used']
    bal_eth_used = bal['ETH']['used']
    bal_fiat_total = bal[currency_f.upper()]['total']
    bal_eth_total = bal['ETH']['total']
    bl = {}
    for i in ('bal_fiat_free',  'bal_fiat_used', 'bal_fiat_total', 'bal_eth_free', 'bal_eth_used', 'bal_eth_total'):
        bl[i] = locals()[i]
    df = pd.DataFrame({k: [v] for k, v in bl.items()})
    return df


basics = get_basic(now)

bl = get_bal(ex, currency_f)
td = get_td(ex)
ob = get_ob(ex, pair)

df = pd.concat([basics, bl, ob], axis=1)


def save_to_sql():
    conn = sqlite3.connect('/Users/Zi/Projects/Dash_eth/test.db')
    table_name = ex + "_bal_orderbook"
    df.to_sql(table_name, conn, if_exists='append')
    conn.close()


save_to_sql()
