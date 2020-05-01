import requests
import pandas as pd
from datetime import datetime
import ccxt
import sqlite3
import config
import settings

now = datetime.utcnow()


def get_fx(currency_f):
    fx = requests.get(
        'https://apilayer.net/api/live?access_key=a1d6d82a3df7cf7882c9dd2b35146d6e&source=USD&format=1').json()
    return fx['quotes']['USD' + currency_f.upper()]


# convert all fee to fiat
def fxy(price, fee):
    cost = fee['cost']
    currency = fee['currency']
    return cost if currency == 'PLN' else cost * price


def parse_indodax(apiInstance, now_ts, currency_f, ex):
    params = {
        'pair': 'eth_idr',
        'count': 50,  # number of trades return
        'end': now_ts
    }
    trades = apiInstance.privatePostTradeHistory(params)['return']['trades']
    df = pd.DataFrame(trades)
    df['time'] = df['trade_time'].apply(
        lambda x: datetime.fromtimestamp(int(x)))
    df = df.rename(columns={'trade_time': 'utc'})

    column_names = ["utc", "time", "trade_id", "order_id", "type",
                    "takerOrMaker", "side", "amount", "price", "fee_fiat", "fx", "fee_pct"]
    df_my = pd.DataFrame(columns=column_names)

    df_my['utc'] = df['utc'].astype(int) * 1000
    df_my['time'] = df['time']
    df_my['trade_id'] = df['trade_id']
    df_my['order_id'] = df['order_id']
    df_my['type'] = None
    df_my['takerOrMaker'] = None
    df_my['side'] = df['type']
    df_my['amount'] = df['eth']
    df_my['price'] = df['price']
    df_my['fee_fiat'] = df['fee']
    df_my['fee_pct'] = df_my['fee_fiat'].astype(
        float) / (df_my['price'].astype(float) * df_my['amount'].astype(float))
    df_my['fx'] = get_fx(currency_f)
    df_my['exchange'] = ex
    return df_my


def parse_normal(apiInstance, currency_f, ex):
    trades = apiInstance.fetch_my_trades()
    df = pd.DataFrame(trades)

    column_names = ["utc", "time", "trade_id", "order_id", "type",
                    "takerOrMaker", "side", "amount", "price", "fee_fiat", "fx", "fee_pct"]
    df_my = pd.DataFrame(columns=column_names)

    df_my['utc'] = df['timestamp']
    df_my['time'] = df['timestamp'].apply(
        lambda x: datetime.fromtimestamp(int(x / 1000)))
    df_my['trade_id'] = df['id']
    df_my['order_id'] = df['order']
    df_my['type'] = df['type']
    df_my['takerOrMaker'] = df['takerOrMaker']
    df_my['side'] = df['side']
    df_my['amount'] = df['amount']
    df_my['price'] = df['price']
    df_my['fee_fiat'] = df.apply(lambda x: fxy(x['price'], x['fee']), axis=1)
    df_my['fee_pct'] = df_my['fee_fiat'] / (df['price'] * df['amount'])
    df_my['fx'] = get_fx(currency_f)
    df_my['exchange'] = ex
    return df_my


def fetcher_trades(exchange, now):
    ex = exchange['name']
    currency_c = 'eth'
    currency_f = exchange['currency']
    now_ts = now.timestamp()
    pair = currency_c.upper() + '/' + currency_f.upper()
    apiInstance = settings.exchanges[ex]['init']

    if ex == 'indodax':
        df_my = parse_indodax(apiInstance, now_ts, currency_f, ex)
    else:
        df_my = parse_normal(apiInstance, currency_f, ex)

    return df_my


def save_to_sql(ex, df):
    conn = sqlite3.connect('/Users/Zi/Projects/Dash_eth/test.db')
    table_name = ex + "_trades"

    # append
    df.to_sql(table_name, conn, if_exists='append')

    # select unique entry in pandas
    df_pre = pd.read_sql_query("SELECT * from {}".format(table_name), conn)
    df_new = df_pre.drop_duplicates(subset=["trade_id"])
    df_new = df_new.sort_values(by=['utc'])
    # replace the previous sql
    df_new.to_sql(table_name, conn, if_exists='replace', index=False,
                  index_label='First')
    conn.close()


exchanges = settings.exchanges

for k, v in exchanges.items():
    exchange_name = k
    exchange = v
    df = fetcher_trades(exchange, now)
    # print(df)
    save_to_sql(exchange_name, df)


#*/1 * * * * /opt/anaconda2/envs/py3/bin/python3 /Users/Zi/Projects/Dash_eth/fetcher_bal_orderbook.py
#*/20 * * * * /opt/anaconda2/envs/py3/bin/python3 /Users/Zi/Projects/Dash_eth/trade_fetcher.py
