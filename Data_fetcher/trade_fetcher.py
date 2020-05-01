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


def get_td(ex):
    ex_instance = eval('ccxt.' + ex)(arg)
    trades = ex_instance.privatePostTradeHistory(params)['return']['trades']
    df = pd.DataFrame(trades)
    df['time'] = df['trade_time'].apply(
        lambda x: datetime.fromtimestamp(int(x)))
    df = df.rename(columns={'trade_time': 'utc'})
    return df


basics = get_basic(now)


td = get_td(ex)

df = get_td(ex)


def save_to_sql():
    conn = sqlite3.connect('/Users/Zi/Projects/Dash_eth/test.db')
    table_name = ex + "_trade"

    # append
    df.to_sql(table_name, conn, if_exists='append')

    # select unique entry in pandas
    df_pre = pd.read_sql_query("SELECT * from {}".format(table_name), conn)
    df_new = df_pre.drop_duplicates(subset=["trade_id"])

    # replace the previous sql
    df_new.to_sql(table_name, conn, if_exists='replace', index=False,
                  index_label='First')
    conn.close()


save_to_sql()
