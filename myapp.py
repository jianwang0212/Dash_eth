import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import colorlover as cl
import datetime as dt
import flask
import os
import pandas as pd
import time
import sqlite3
import numpy as np
import math


app = dash.Dash()


# data

conn = sqlite3.connect('/Users/Zi/Projects/Dash_eth/test.db')
df1 = pd.read_sql_query("SELECT * from indodax_merge_td_bal_ods", conn)
df2 = pd.read_sql_query("SELECT * from indodax_open_order", conn)
df3 = pd.read_sql_query("SELECT * from indodax_trades", conn)
conn.close()
# setup
data = []
rgba_bid = ['rgba(132, 132, 239, .9)',
            'rgba(28, 28, 221, .7)',
            'rgba(28, 28, 221, .5)',
            'rgba(28, 28, 221, .4)',
            'rgba(28, 28, 221, .2)']

rgba_ask = ['rgba(221, 28, 86, .9)',
            'rgba(221, 28, 86, .7)',
            'rgba(221, 28, 86, .5)',
            'rgba(221, 28, 86, .4)',
            'rgba(221, 28, 86, .2)']

rgba_bal = ['rgba(10, 10, 162, .9)',
            'rgba(10, 10, 162, .4)',
            'rgba(235, 64, 52, .9)',
            'rgba(235, 64, 52, .4)']


# Open orders: create buy & sell column
for side in ['buy', 'sell']:
  df2[side + '_OpenOrder_price'] = df2['OpenOrder_price']
  condition = df2['OpenOrder_side'] != side
  df2.loc[condition, side + '_OpenOrder_price'] = None

# Trades: create buy & sell column
for side in ['buy', 'sell']:
  df1[side + '_executed'] = df1['price']
  condition = df1['side'] != side
  df1.loc[condition, side + '_executed'] = None


# Graph - setup traces

# Market orderbook
for i in [1]:
  trace_bid = go.Scatter(x=df1['time_x'],
                         y=df1[str(i) + '_bid_px'],
                         name='bid_' + str(i),
                         line={"shape": 'hv'},
                         marker_color=rgba_bid[i - 1],
                         customdata=df1[str(i) + '_bid_sz'],
                         hovertemplate="mkt_px:" + "%{y}; "
                         "sz:" + "%{customdata:.3f}<br>"
                         )
  trace_ask = go.Scatter(x=df1['time_x'],
                         y=df1[str(i) + '_ask_px'],
                         name='ask_' + str(i),
                         line={"shape": 'hv'},
                         marker_color=rgba_ask[i - 1],
                         customdata=df1[str(i) + '_ask_sz'],
                         hovertemplate="mkt_px:" + "%{y}; "
                         "sz:" + "%{customdata:.3f}<br>"
                         )

# My open orders
trace_open_orders_buy = go.Scatter(x=df2['time'],
                                   y=df2['buy_OpenOrder_price'],
                                   mode='markers',
                                   name='my_bid',
                                   opacity=0.8,
                                   marker=dict(color='Yellow',
                                               size=10,
                                               opacity=0.6,
                                               symbol='line-ew',
                                               line=dict(
                                                   color='LightSkyBlue',
                                                   width=4)),
                                   hovertemplate="my_bid:" + "%{y}"


                                   )
trace_open_orders_sell = go.Scatter(x=df2['time'],
                                    y=df2['sell_OpenOrder_price'],
                                    mode='markers',
                                    name='my_ask',
                                    opacity=0.8,
                                    marker=dict(color='gold',
                                                size=10,
                                                opacity=0.6,
                                                symbol='line-ew',
                                                line=dict(
                                                    color='violet',
                                                    width=4)),
                                    hovertemplate="my_ask:" + "%{y}"


                                    )

# My trades
# my trades - marker setup: create a size var for marker
sz = df1['amount'].tolist()
sz1 = [0 if pd.isnull(x) else math.log10(float(x) + 10) * 5 for x in sz]


trace_trades_buy = go.Scatter(x=df1['time_x'],
                              y=df1['buy_executed'],
                              name='bid_executed',
                              mode='markers',
                              marker=dict(color='LightSkyBlue',
                                          size=sz1,
                                          line=dict(
                                              color='blue',
                                              width=2)
                                          ),
                              marker_symbol='triangle-up',

                              customdata=df1['amount'],
                              hovertemplate="buy_px:" + "%{y}; "
                              "sz:" + "%{customdata}<br>"
                              )
trace_trades_sell = go.Scatter(x=df1['time_x'],
                               y=df1['sell_executed'],
                               name='ask_executed',
                               mode='markers',
                               marker=dict(color='LightSkyBlue',
                                           size=sz1,
                                           line=dict(
                                               color='red',
                                               width=2)
                                           ),
                               marker_symbol='triangle-down',

                               customdata=df1['amount'],
                               hovertemplate="sell_px:" + "%{y}; "
                               "sz:" + "%{customdata}<br>"
                               )


# balance
trace_bal_ff = go.Bar(x=df1['time_x'],
                      y=df1['bal_fiat_free'] / df1['1_bid_px'],
                      name='bal_fiat_free',
                      marker_color=rgba_bal[0])

trace_bal_fu = go.Bar(x=df1['time_x'],
                      y=df1['bal_fiat_used'] / df1['1_bid_px'],
                      name='bal_fiat_used',
                      marker_color=rgba_bal[1])
trace_bal_ef = go.Bar(x=df1['time_x'],
                      y=df1['bal_eth_free'],
                      name='bal_eth_free',
                      marker_color=rgba_bal[2])
trace_bal_eu = go.Bar(x=df1['time_x'],
                      y=df1['bal_eth_used'],
                      name='bal_eth_used',
                      marker_color=rgba_bal[3])


trace_bal_all = go.Scatter(x=df1['time_x'],
                           y=(df1['bal_eth_total'] * df1['1_bid_px'] +
                              df1['bal_fiat_total']) / df1['fx_x'],
                           name='bal_all($)')

# Group traces to fig
fig1_sub1_traces = [trace_bid, trace_ask, trace_open_orders_buy, trace_open_orders_sell,
                    trace_trades_buy, trace_trades_sell]
fig1_sub2_traces = [trace_bal_ff, trace_bal_fu,
                    trace_bal_ef, trace_bal_eu]

fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                     specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
                     subplot_titles=("Market orderbook & my orders/trades", "My total balance & holding position"))

for i in range(len(fig1_sub1_traces)):
  fig1.add_trace(fig1_sub1_traces[i],
                 row=1, col=1)

for i in range(len(fig1_sub2_traces)):
  fig1.add_trace(fig1_sub2_traces[i],
                 row=2, col=1)
fig1.add_trace(trace_bal_all,
               row=2, col=1, secondary_y=True)
fig1.update_layout(barmode='stack')

# Fig 2 Current dash board
# Bal pie chart
pie_labels = ['fiat_free', 'fiat_used', 'eth_free', 'eth_used']
pie_values = [df1['bal_fiat_free'].iloc[-1] / df1['1_bid_px'].iloc[-1], df1['bal_fiat_used'].iloc[-1] / df1['1_bid_px'].iloc[-1],
              df1['bal_eth_free'].iloc[-1], df1['bal_eth_used'].iloc[-1]]

trace_pie_bal = go.Pie(
    labels=pie_labels, values=pie_values, title='Balance in ETH', hole=0.4,
    textinfo='label+percent')


# order book info

boop = df2['buy_OpenOrder_price']
c_boop = boop.loc[~boop.isnull()].iloc[-1]
soop = df2['sell_OpenOrder_price']
c_soop = soop.loc[~soop.isnull()].iloc[-1]

ob_y_bid = [df1['1_bid_px'].iloc[-1], df1['2_bid_px'].iloc[-1],
            df1['3_bid_px'].iloc[-1], df1['4_bid_px'].iloc[-1], df1['5_bid_px'].iloc[-1]]
ob_y_ask = [df1['1_ask_px'].iloc[-1], df1['2_ask_px'].iloc[-1],
            df1['3_ask_px'].iloc[-1], df1['4_ask_px'].iloc[-1], df1['5_ask_px'].iloc[-1]]


trace_c_ords_bid = go.Scatter(
    x=[1] * len(ob_y_bid), y=ob_y_bid, mode="markers", marker_symbol='line-ew',
    marker_line_color="midnightblue", marker_color="lightskyblue",
    marker_line_width=3, marker_size=150, name='mkt_bid')

trace_c_ords_ask = go.Scatter(
    x=[1] * len(ob_y_ask), y=ob_y_ask, mode="markers", marker_symbol='line-ew',
    marker_line_color="red", marker_color="red",
    marker_line_width=3, marker_size=150, name='mkt_ask')


trace_c_ords_my_bid = go.Scatter(
    x=[1], y=[c_boop], mode="markers", marker_symbol='diamond-wide',
    marker_line_color="gold", marker_color="blue",
    marker_line_width=2, marker_size=15, name='my_bid')

trace_c_ords_my_ask = go.Scatter(
    x=[1], y=[c_soop], mode="markers", marker_symbol='diamond-wide',
    marker_line_color="gold", marker_color="red",
    marker_line_width=2, marker_size=15, name='my_ask')


fig2 = make_subplots(rows=1, cols=2,
                     specs=[[{"type": "domain"}, {"type": "xy"}]],
                     subplot_titles=("Holdings", "Order book position"))
fig2.add_trace(trace_pie_bal, row=1, col=1)
fig2.add_trace(trace_c_ords_bid, row=1, col=2)
fig2.add_trace(trace_c_ords_ask, row=1, col=2)
fig2.add_trace(trace_c_ords_my_bid, row=1, col=2)
fig2.add_trace(trace_c_ords_my_ask, row=1, col=2)

fig2.update_layout(title='Current orders and positions')

# Tables

tbl_my_trades = df3[['time', 'type', 'type', 'takerOrMaker', 'side', 'amount', 'price',
                     'fee_fiat', 'fee_pct']]

tbl_my_orders = df2[['time', 'OpenOrder_side', 'OpenOrder_price',
                     'OpenOrder_amount', 'OpenOrder_filled', 'OpenOrder_remaining',
                     'OpenOrder_fee']]
tbl_my_trades = tbl_my_trades.tail().iloc[::-1]
tbl_my_orders = tbl_my_orders.tail().iloc[::-1]
# plot
app.layout = html.Div(children=[
    html.H1('Trading Dashboard'),
    dcc.Graph(id='g1',
              figure=fig1),
    dcc.Graph(id='g2',
              figure=fig2),
    html.H2('My latest trades'),
    dash_table.DataTable(id='table_trades',
                         columns=[{"name": i, "id": i}
                                  for i in tbl_my_trades.columns],
                         data=tbl_my_trades.to_dict('records'),
                         style_as_list_view=True,
                         style_cell={'padding': '5px'},
                         style_header={
                             'backgroundColor': 'white',
                             'fontWeight': 'bold'
                         }),
    html.H2('My latest open orders'),
    dash_table.DataTable(id='table_openorders',
                         columns=[{"name": i, "id": i}
                                  for i in tbl_my_orders.columns],
                         data=tbl_my_orders.to_dict('records'),
                         style_as_list_view=True,
                         style_cell={'padding': '5px'},
                         style_header={
                             'backgroundColor': 'white',
                             'fontWeight': 'bold'
                         })

]
)

# server = app.server

# app.scripts.config.serve_locally = False


# colorscale = cl.scales['9']['qual']['Paired']

# df = pd.read_csv(
#     'https://raw.githubusercontent.com/plotly/datasets/master/dash-stock-ticker-demo.csv')

# conn = sqlite3.connect('test.db')
# df1 = pd.read_sql_query("SELECT * from bitbay_bal_orderbook", conn)
# print(df1)

# app.layout = html.Div([
#     html.Div([
#         html.H2('Finance Explorer',
#                 style={'display': 'inline',
#                        'float': 'left',
#                        'font-size': '2.65em',
#                        'margin-left': '7px',
#                        'font-weight': 'bolder',
#                        'font-family': 'Product Sans',
#                        'color': "rgba(117, 117, 117, 0.95)",
#                        'margin-top': '20px',
#                        'margin-bottom': '0'
#                        }),
#         # html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
#         #         style={
#         #             'height': '100px',
#         #             'float': 'right'
#         #         },
#         # ),
#     ]),
#     dcc.Dropdown(
#         id='stock-ticker-input',
#         options=[{'label': s[0], 'value': str(s[1])}
#                  for s in zip(df.Stock.unique(), df.Stock.unique())],
#         value=['GOOGL'],
#         multi=True
#     ),
#     html.Div(id='graphs')
# ], className="container")


# def bbands(price, window_size=10, num_of_std=5):
#     rolling_mean = price.rolling(window=window_size).mean()
#     rolling_std = price.rolling(window=window_size).std()
#     upper_band = rolling_mean + (rolling_std * num_of_std)
#     lower_band = rolling_mean - (rolling_std * num_of_std)
#     return rolling_mean, upper_band, lower_band


# @app.callback(
#     dash.dependencies.Output('graphs', 'children'),
#     [dash.dependencies.Input('stock-ticker-input', 'value')])
# def update_graph(tickers):
#     graphs = []

#     if not tickers:
#         graphs.append(html.H3(
#             "Select a stock ticker.",
#             style={'marginTop': 20, 'marginBottom': 20}
#         ))
#     else:
#         for i, ticker in enumerate(tickers):

#             dff = df1

#             candlestick = {
#                 'x': dff['time'],
#                 'open': dff['1_bid_px'],
#                 'high': dff['1_bid_px'],
#                 'low': dff['1_bid_px'],
#                 'close': dff['1_bid_px'],
#                 'type': 'candlestick',
#                 'name': ticker,
#                 'legendgroup': ticker,
#                 'increasing': {'line': {'color': colorscale[0]}},
#                 'decreasing': {'line': {'color': colorscale[1]}}
#             }
#             bb_bands = bbands(dff['1_bid_px'])
#             bollinger_traces = [{
#                 'x': dff['time'], 'y': y,
#                 'type': 'scatter', 'mode': 'lines',
#                 'line': {'width': 1, 'color': colorscale[(i * 2) % len(colorscale)]},
#                 'hoverinfo': 'none',
#                 'legendgroup': ticker,
#                 'showlegend': True if i == 0 else False,
#                 'name': '{} - bollinger bands'.format(ticker)
#             } for i, y in enumerate(bb_bands)]
#             graphs.append(dcc.Graph(
#                 id=ticker,
#                 figure={
#                     'data': [candlestick] + bollinger_traces,
#                     'layout': {
#                         'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
#                         'legend': {'x': 0}
#                     }
#                 }
#             ))

#     return graphs


if __name__ == '__main__':
  app.run_server(debug=True)
