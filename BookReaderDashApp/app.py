import re
from datetime import datetime as dt

from flask_caching import Cache

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import dash
from dash.dependencies import Input, Output
from utils.data_workflow import load_data
import plotly.express as px
from app_layout import generate_app_layout
from settings import HOVER_TEMPLATES, EMPTY_TEMPLATE
from utils import generate_colors

columns_to_display = ['time', 'date', 'bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz', 'direction']

data_files = ['data_line_btc_full.data', 'data_line_btc.data', 'data_lines.data', 'data_lines_big.data',
              'data_top_btc_full.csv', 'data_top.csv', 'data_top_big.csv']

# Choose a file from list
# btc data is on October 16 2019, given data is August 7 2019
file_to_load = data_files[0]
df = load_data(file_to_load, use_cache=True)

features = [
    {"label": "Bid Size", "value": "bidSz"},
    {"label": "Bid Price", "value": "bidPx"},
    {"label": "Ask Size", "value": "askSz"},
    {"label": "Ask Price", "value": "askPx"},
    {"label": "Spread", "value": "spread"},
]

ranges = {
    'hour': [0, 24],
    'minute': [0, 60],
    'second': [0, 60],
    'microsecond': [0, 1000000]
}
msuks = df['msuk'].unique()

app = dash.Dash(__name__)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

app.layout = generate_app_layout(msuks, features)


@app.callback([Output('table', 'data'), Output('time_series', 'figure'),
               Output('bid_ask', 'figure'), Output('depth', 'figure'),
               Output('size_imbalance', 'figure'), Output('filtered_df', 'children')],
              [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value'),
               Input('date_picker', 'date'), Input('msuk_selector', 'value'),
               Input('feature_selector', 'value')])
@cache.memoize(timeout=20)
def update_figure(hour_value, minute_value, second_value, micros_value, date, msuk, feature):
    filtered_df = df.copy()

    if msuk is not None:
        filtered_df = filtered_df[(filtered_df.msuk == msuk)]
    if date is not None:
        date = dt.strptime(re.split(r"[T ]", date)[0], '%Y-%m-%d')
        date = dt.date(date)
        filtered_df = filtered_df[(filtered_df.date == date)]

    filtered_df = filter_dataframe(filtered_df, 'hour', hour_value)
    filtered_df = filter_dataframe(filtered_df, 'minute', minute_value)
    filtered_df = filter_dataframe(filtered_df, 'second', second_value)
    filtered_df = filter_dataframe(filtered_df, 'microsecond', micros_value)

    df_to_display = filtered_df[columns_to_display].to_dict('records')
    bid_ask_df = filtered_df.drop_duplicates(subset='datetime')

    figure = generate_figure(bid_ask_df, feature)
    bid_ask_fig = generate_bid_ask_figure(bid_ask_df)
    depth_fig = generate_depth_cum_figure(filtered_df)
    size_imbalance_fig = generate_size_imbalance_figure(bid_ask_df)
    depth_fig_2_json = filtered_df.to_json(date_format='iso', orient='split')

    return df_to_display, figure, bid_ask_fig, depth_fig, size_imbalance_fig, depth_fig_2_json

def filter_dataframe(df, attr, range):
    if range is not None and range != ranges[attr]:
        min_value, max_value = range
        return df[(df[attr] <= max_value) & (df[attr] >= min_value)]
    else:
        return df

def generate_figure(relevant_df, feature):
    fig = px.line(relevant_df, x="datetime", y=feature, template='plotly_white')
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def generate_bid_ask_figure(relevant_df):
    fig = make_subplots(rows=2, cols=1,shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.7, 0.3])
    dt = relevant_df["datetime"]
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["bidPx"], name='Bid', mode='lines', line_color='green'
                             ), row=1, col=1)
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["askPx"], name='Ask', fill='tonexty', mode='lines', line_color='red'), row=1, col=1)

    fig.add_trace(go.Scatter(x=dt, y=relevant_df["bidSz"], name='Bid Volume', mode='lines', line_color='green'), row=2, col=1)
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["askSz"], name='Ask Volume', mode='lines', line_color='red'), row=2, col=1)
    fig.update_layout(title_text="Bid Ask and Volumes", legend_orientation="h", template='plotly_white', hovermode='x unified')
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def generate_depth_cum_figure(df):
    data = df[['datetime', 'cumulative_trade_volume', 'tradePx']].set_index(['tradePx', 'datetime']).unstack()
    x = df['datetime'].drop_duplicates()
    y = data.index
    z = data.values
    fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y, hovertemplate=HOVER_TEMPLATES['depth_figure']))
    best_df = df.drop_duplicates('datetime')
    bid, ask = best_df['bidPx'], best_df['askPx']
    fig.add_trace(go.Scatter(x=x, y=bid, name='Bid', mode='lines', line_color='green', hovertemplate=HOVER_TEMPLATES['line']))
    fig.add_trace(go.Scatter(x=x, y=ask, name='Ask', mode='lines', line_color='red', hovertemplate=HOVER_TEMPLATES['line']))
    fig.update_layout(title_text="Cumulative volumes per price", template='plotly_white')
    fig.update_xaxes(showspikes=True, spikemode="across")
    return fig


@app.callback(Output('depth_2', 'figure'),
              [Input('filtered_df', 'children'), Input('color_scale', 'value')])
def generate_depth_figure_non_cum(df, scale):
    df = pd.read_json(df, orient='split')
    data = df[['datetime', 'tradeSz', 'tradePx']].set_index(['tradePx', 'datetime']).unstack()
    x = df['datetime'].drop_duplicates()
    y = data.index
    z = data.values
    max_val = np.nanmax(z)
    colorscale, colorbar = generate_colors(max_val, scale)
    fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y, hovertemplate=HOVER_TEMPLATES['depth_figure'],
                                    colorscale=colorscale, colorbar=colorbar))
    best_df = df.drop_duplicates('datetime')
    bid, ask = best_df['bidPx'], best_df['askPx']
    fig.add_trace(go.Scatter(x=x, y=bid, name='Bid', mode='lines', line_color='green', hovertemplate=HOVER_TEMPLATES['line']))
    fig.add_trace(go.Scatter(x=x, y=ask, name='Ask', mode='lines', line_color='red', hovertemplate=HOVER_TEMPLATES['line']))
    fig.update_layout(title_text="Volumes per price", template='plotly_white')
    fig.update_xaxes(showspikes=True, spikemode="across")

    return fig

# TODO: generate lines for different levels (not just best)
def generate_size_imbalance_figure(relevant_df):
    fig = px.line(relevant_df, x="datetime", y='size_imbalance', template='plotly_white')
    return fig

@app.callback(
    Output('depth_detail', 'figure'),
    [Input('depth_2', 'clickData'), Input('depth', 'clickData')])
def display_click_data(clickData_2, clickData):
    fig = go.Figure()
    ctx = dash.callback_context
    if not ctx.triggered:
        draft_template = go.layout.Template()
        draft_template.layout.annotations = [EMPTY_TEMPLATE]
        fig.update_layout(template=draft_template)
    else:
        datetime = ctx.triggered[0]['value']['points'][0].get('x', None)
        filtered_df = df[df['datetime'] == datetime][['direction', 'tradeSz', 'tradePx']]
        ask, bid = filtered_df[filtered_df['direction']=='Sell'], filtered_df[filtered_df['direction']=='Buy']
        ask_prices, ask_sizes = ask['tradePx'], ask['tradeSz']
        bid_prices, bid_sizes = bid['tradePx'], bid['tradeSz']
        fig = go.Figure(data=[
                go.Bar(name='Ask', x=ask_prices, y=ask_sizes, marker_color='red', hovertemplate=HOVER_TEMPLATES['trade_volume_detail']),
                go.Bar(name='Bid', x=bid_prices, y=bid_sizes, marker_color='green', hovertemplate=HOVER_TEMPLATES['trade_volume_detail'])
        ])
        fig.update_layout(title=f'Trade Volumes for: {datetime}', template='plotly_white')

    return fig

@app.callback(
    Output('output_timeframe', 'children'),
    [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
     Input('second_slider', 'value'), Input('micros_slider', 'value'),
     Input('date_picker', 'date')])
@cache.memoize(timeout=20)
def generate_output_timeframe(hour_value, minute_value, second_value, micros_value, date):
    is_hour_range = hour_value[0] < hour_value[1]
    is_minute_range = minute_value[0] < minute_value[1]
    is_second_range = second_value[0] < second_value[1]
    if is_hour_range:
        return f'Selected Timeframe: {date.split()[0]} {hour_value[0]}-{hour_value[1]} h'
    elif is_minute_range:
        return f'Selected Timeframe: {date.split()[0]} {hour_value[0]}h {minute_value[0]}-{minute_value[1]}min'
    elif is_second_range:
        return f'Selected Timeframe: {date.split()[0]} {hour_value[0]}h {minute_value[0]}min {second_value[0]}-{second_value[1]}s'
    else:
        return f'Selected Timeframe: {date.split()[0]} {hour_value[0]}h {minute_value[0]}min {second_value[0]}s {micros_value}ms'


@app.callback(
    Output('hour_slider', 'value'),
    [Input('all_hour', 'on'), ])
def set_hour_values(button):
    return [0, 24] if button else [6, 10]


@app.callback(
    [Output('minute_slider', 'value'), Output('minute_slider', 'disabled')],
    [Input('all_min', 'on'), Input('hour_slider', 'value')])
def set_min_values(button, value):
    is_hour_range = value[0] < value[1]
    return ([0, 60], is_hour_range) if (button or is_hour_range) else ([4, 10], is_hour_range)


@app.callback(
    [Output('second_slider', 'value'), Output('second_slider', 'disabled')],
    [Input('all_second', 'on'), Input('minute_slider', 'value')])
def set_sec_values(button, value):
    is_minute_range = value[0] < value[1]
    return ([0, 60], is_minute_range) if (button or is_minute_range) else ([5, 30], is_minute_range)


@app.callback(
    [Output('micros_slider', 'value'), Output('micros_slider', 'disabled')],
    [Input('all_micros', 'on'), Input('second_slider', 'value')])
def set_micros_values(button, value):
    is_second_range = value[0] < value[1]
    return ([0, 1000000], is_second_range) if (button or is_second_range) else ([597045, 650000], is_second_range)


if __name__ == '__main__':
    app.run_server(debug=True)
