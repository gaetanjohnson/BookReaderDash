import re
from datetime import datetime as dt

from flask_caching import Cache
import pandas as pd
import dash
from dash.dependencies import Input, Output
from utils.data_workflow import load_data as load_data_workflow
from app_layout import generate_app_layout
from utils.figure_configs import FigureGenerator
from utils.settings import FEATURES, TIME_RANGES, COLUMNS_FOR_DATA_TABLE
from settings.settings import DATA_FILES


# btc data is on October 16 2019, given data is August 7 2019

app = dash.Dash(__name__)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

app.layout = generate_app_layout(FEATURES, DATA_FILES)


"""
The three next functions handle loading the data from disk, but only when a different file is selected.
Data is cached and rapidly accessible to other callbacks 
"""


@cache.memoize()
def global_store(file_path):
    print(f'Loading data from {file_path}')
    df = load_data_workflow(file_path, use_cache=True)
    msuks = df['msuk'].unique()
    options = [{'label': msuk, 'value': msuk} for msuk in msuks]
    print('Data Loaded')
    return df, options


@app.callback([Output('signal_data_ready', 'children'), Output('msuk_selector', 'options')],
              [Input('file', 'value')])
def load_data_from_file_selector(file_path):
    msuks_options = global_store(file_path)[1]
    return file_path, msuks_options


def get_data_from_cache(file_path):
    data = global_store(file_path)[0]
    return data


"""
Next callback filters the dataframe for selected timeframe, generates appropriate figures and stores filtered_dataframe
"""


@app.callback([Output('table', 'data'), Output('time_series', 'figure'),
               Output('bid_ask', 'figure'), Output('depth', 'figure'),
               Output('size_imbalance', 'figure'), Output('filtered_df', 'children')],
              [Input('signal_data_ready', 'children'), Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value'),
               Input('date_picker', 'date'), Input('msuk_selector', 'value'),
               Input('feature_selector', 'value')])
@cache.memoize(timeout=20)
def update_figure(file_path, hour_value, minute_value, second_value, micros_value, date, msuk, feature):
    # filtered_df = df.copy()
    filtered_df = get_data_from_cache(file_path)
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
    df_to_display = filtered_df[COLUMNS_FOR_DATA_TABLE].to_dict('records')
    bid_ask_df = filtered_df.drop_duplicates(subset='datetime')

    figure = FigureGenerator.figure(bid_ask_df, feature)
    bid_ask_fig = FigureGenerator.bid_ask_figure(bid_ask_df)
    depth_fig = FigureGenerator.depth_cum_figure(filtered_df)
    size_imbalance_fig = FigureGenerator.size_imbalance_figure(bid_ask_df)
    filtered_df_json = filtered_df.to_json(date_format='iso', orient='split')

    return df_to_display, figure, bid_ask_fig, depth_fig, size_imbalance_fig, filtered_df_json


def filter_dataframe(df, attr, timerange):
    if timerange is not None and timerange != TIME_RANGES[attr]:
        min_value, max_value = timerange
        return df[(df[attr] <= max_value) & (df[attr] >= min_value)]
    else:
        return df


"""
Generates the depth figure from filtered df json. It is separate from the above for quick load on color scale change
"""


@app.callback(Output('depth_2', 'figure'),
              [Input('filtered_df', 'children'), Input('color_scale', 'value')])
def generate_depth_figure_non_cum(df, scale):
    df = pd.read_json(df, orient='split')
    fig = FigureGenerator.depth_non_cum_figure(df, scale)
    return fig


"""
Generates trade_volume_details figure on clicking the depth figures
"""


@app.callback(
    Output('depth_detail', 'figure'),
    [Input('depth_2', 'clickData'), Input('depth', 'clickData'), Input('signal_data_ready', 'children')])
def display_click_data(click_data_2, click_data, file_path):
    ctx = dash.callback_context
    filtered_df = get_data_from_cache(file_path)
    fig = FigureGenerator.trade_volume_detail(ctx, filtered_df)
    return fig


"""
Callback to display selected timeframe
"""


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
        return f'Selected Timeframe: {date.split()[0]} {hour_value[0]}h {minute_value[0]}min ' \
               f'{second_value[0]}-{second_value[1]}s'
    else:
        return f'Selected Timeframe: {date.split()[0]} {hour_value[0]}h {minute_value[0]}min ' \
               f'{second_value[0]}s {micros_value}ms'


"""
Below we have simple callbacks for disabling time sliders when slider above is a range (as opposed to a single value)
"""


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
