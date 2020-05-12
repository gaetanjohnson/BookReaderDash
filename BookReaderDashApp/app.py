import re
from datetime import datetime as dt

from flask_caching import Cache
import pandas as pd
import dash
from dash.dependencies import Input, Output
from utils.data_workflow import load_data
from app_layout import generate_app_layout
from utils.figure_configs import FigureGenerator


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

    figure = FigureGenerator.figure(bid_ask_df, feature)
    bid_ask_fig = FigureGenerator.bid_ask_figure(bid_ask_df)
    depth_fig = FigureGenerator.depth_cum_figure(filtered_df)
    size_imbalance_fig = FigureGenerator.size_imbalance_figure(bid_ask_df)
    depth_fig_2_json = filtered_df.to_json(date_format='iso', orient='split')

    return df_to_display, figure, bid_ask_fig, depth_fig, size_imbalance_fig, depth_fig_2_json


def filter_dataframe(df, attr, range):
    if range is not None and range != ranges[attr]:
        min_value, max_value = range
        return df[(df[attr] <= max_value) & (df[attr] >= min_value)]
    else:
        return df


@app.callback(Output('depth_2', 'figure'),
              [Input('filtered_df', 'children'), Input('color_scale', 'value')])
def generate_depth_figure_non_cum(df, scale):
    df = pd.read_json(df, orient='split')
    fig = FigureGenerator.depth_non_cum_figure(df, scale)
    return fig


@app.callback(
    Output('depth_detail', 'figure'),
    [Input('depth_2', 'clickData'), Input('depth', 'clickData')])
def display_click_data(clickData_2, clickData):
    ctx = dash.callback_context
    fig = FigureGenerator.trade_volume_detail(ctx, df)
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
