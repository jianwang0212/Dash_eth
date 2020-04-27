import sqlite3
import pandas as pd
import settings
from datetime import datetime

# trades check
exchanges = settings.exchanges


for k, v in exchanges.items():
    exchange_name = k
    exchange = v
    table_name = exchange_name + "_trades"
    conn = sqlite3.connect('/Users/Zi/Projects/Dash_eth/test.db')
    df_td = pd.read_sql_query("SELECT * from {}".format(table_name), conn)
    xt = df_td["utc"].apply(lambda x: datetime.fromtimestamp(int(x) / 1e3))
    df_td['time_mts'] = xt.apply(lambda x: str(x.strftime("%y-%m-%d %H:%M")))

    table_name = exchange_name + "_bal_orderbook"

    df_ba = pd.read_sql_query("SELECT * from {}".format(table_name), conn)
    xt = df_ba["utc"].apply(lambda x: datetime.fromtimestamp(int(x)))
    df_ba['time_mts'] = xt.apply(lambda x: str(x.strftime("%y-%m-%d %H:%M")))
    df_merge = pd.merge(df_ba, df_td, how='left', on=['time_mts'])

    print(df_merge)
    table_name = exchange_name + "_merge_td_bal_ods"

    df_merge.to_sql(table_name, conn, if_exists='replace', index=False,
                    index_label='First')
    conn.close()
