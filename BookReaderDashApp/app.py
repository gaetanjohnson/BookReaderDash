import re
from datetime import datetime as dt

from flask_caching import Cache

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
from dash.dependencies import Input, Output
from utils.data_workflow import load_data
import plotly.express as px
from app_layout import generate_app_layout

columns_to_display = ['time', 'date', 'bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz', 'direction']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


data_files = ['data_line_btc.data', 'data_lines.data', 'data_lines_big.data',
              'data_top_btc_full.csv', 'data_top.csv', 'data_top_big.csv']

# Choose a file from list
file_to_load = data_files[1]
df = load_data(file_to_load, use_cache=False)

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
               Output('bid_ask', 'figure'), Output('depth', 'figure')],
              [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value'),
               Input('date_picker', 'date'), Input('msuk_selector', 'value'),
               Input('feature_selector', 'value')])
@cache.memoize(timeout=20)
def update_figure(hour_value, minute_value, second_value, micros_value, date, msuk, feature):
    filtered_df = df.copy()
    if date is not None:
        date = dt.strptime(re.split(r"[T ]", date)[0], '%Y-%m-%d')
        date = dt.date(date)
        filtered_df = filtered_df[(filtered_df.date == date)]
    if hour_value is not None and hour_value != ranges['hour']:
        min_hour, max_hour = hour_value
        filtered_df = filtered_df[(filtered_df.hour <= max_hour) & (filtered_df.hour >= min_hour)]
    if minute_value is not None and minute_value != ranges['minute']:
        min_minute, max_minute = minute_value
        filtered_df = filtered_df[(filtered_df.minute <= max_minute) & (filtered_df.minute >= min_minute)]
    if second_value is not None and second_value != ranges['second']:
        min_second, max_second = second_value
        filtered_df = filtered_df[(filtered_df.second <= max_second) & (filtered_df.second >= min_second)]
    if micros_value is not None and micros_value != ranges['microsecond']:
        min_micros, max_micros = micros_value
        filtered_df = filtered_df[(filtered_df.microsecond <= max_micros) & (filtered_df.microsecond >= min_micros)]
    if msuk is not None:
        filtered_df = filtered_df[(filtered_df.msuk == msuk)]
    df_to_display = filtered_df[columns_to_display].to_dict('records')
    figure = generate_figure(filtered_df, feature)

    bid_ask_fig = generate_bid_ask_figure(filtered_df)

    depth_fig = generate_depth_figure(filtered_df)
    return df_to_display, figure, bid_ask_fig, depth_fig


def generate_figure(df, feature):
    fig = px.line(df, x="datetime", y=feature)
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def generate_bid_ask_figure(df):
    relevant_df = df.drop_duplicates(subset='datetime')
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.7, 0.3])
    dt = relevant_df["datetime"]
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["bidPx"], name='Bid', mode='lines', line_color='red'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["askPx"], name='Ask', fill='tonexty', mode='lines', line_color='green'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["bidSz"], name='Bid Volume', mode='lines', line_color='red'), row=2, col=1)
    fig.add_trace(go.Scatter(x=dt, y=relevant_df["askSz"], name='Ask Volume', mode='lines', line_color='green'), row=2, col=1)
    fig.update_layout(title_text="Bid Ask and Volumes", legend_orientation="h")
    fig.update_xaxes(rangeslider_visible=False)
    return fig

def generate_depth_figure(df):
    data = df[['datetime', 'cumulative_trade_volume', 'tradePx']].set_index(['tradePx', 'datetime']).unstack()
    x = df['datetime'].drop_duplicates()
    y = data.index
    z = data.values
    fig = go.Figure(data=go.Contour(z=z, x=x, y=y))
    bid = df.drop_duplicates('datetime')['bidPx']
    fig.add_trace(go.Scatter(x=x, y=bid, name='Bid', mode='lines', line_color='red'))
    fig.update_layout(title_text="Cumulative volumes per price")
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
