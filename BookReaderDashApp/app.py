import logging
import dash
import click
from flask_caching import Cache
from dash.dependencies import Input, Output

from utils import FigureGenerator
from utils import FEATURES, TIME_RANGES, COLUMNS_FOR_DATA_TABLE, APP_INPUTS
from utils.data_workflow import get_filtered_data, get_global_data
from settings import DATA_FILES
from app_layout import generate_app_layout



app = dash.Dash(__name__)


cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})





@app.callback([Output('signal_data_ready', 'children'), Output('msuk_selector', 'options')],
              [Input('file', 'value'), Input('use_cache', 'children')])
def load_data_from_file_selector(file_path, use_cache):
    """
    Handles loading the data from disk, but only when a different file is selected.
    Data is cached for quick use by filtering function.
    """
    _, msuks_options =  get_global_data(file_path, use_cache)
    return file_path, msuks_options


@app.callback(Output('signal_data_filtered', 'children'),
              [Input('signal_data_ready', 'children'), Input('date_picker', 'date'),
               Input('msuk_selector', 'value'), Input('use_cache', 'children'),
               Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value'),])
def filter_dataframe(file_path, *args):
    """
    Handles filtering data from loaded data. Data is cached and rapidly accessible to other callbacks
    """
    _ = get_filtered_data(file_path, *args)
    return file_path



@app.callback([Output('table', 'data'), Output('time_series', 'figure'),
               Output('bid_ask', 'figure'), Output('depth', 'figure'),
               Output('size_imbalance', 'figure')],
              [Input('feature_selector', 'value'), Input('signal_data_filtered', 'children'),
               Input('date_picker', 'date'), Input('msuk_selector', 'value'), Input('use_cache', 'children'),
               Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value')])
def update_figure(feature, *args):
    """
    Updates figure from filtered data
    """
    filtered_df = get_filtered_data(*args)
    bid_ask_df = filtered_df.drop_duplicates(subset='datetime')

    df_to_display = filtered_df[COLUMNS_FOR_DATA_TABLE].to_dict('records')
    figure = FigureGenerator.figure(bid_ask_df, feature)
    bid_ask_fig = FigureGenerator.bid_ask_figure(bid_ask_df)
    depth_fig = FigureGenerator.depth_cum_figure(filtered_df)
    size_imbalance_fig = FigureGenerator.size_imbalance_figure(bid_ask_df)

    app.logger.info("Data loaded for figure updates.")
    return df_to_display, figure, bid_ask_fig, depth_fig, size_imbalance_fig


@app.callback(Output('depth_2', 'figure'),
              [Input('color_scale', 'value'), Input('signal_data_filtered', 'children'),
               Input('date_picker', 'date'), Input('msuk_selector', 'value'), Input('use_cache', 'children'),
               Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value')])
def generate_depth_figure_non_cum(scale, *args):
    """
    Generates the depth figure from filtered data.
    Separate from main figure updater for quick load on color scale change
    """
    df = get_filtered_data(*args)
    fig = FigureGenerator.depth_non_cum_figure(df, scale)
    return fig


@app.callback(
    Output('depth_detail', 'figure'),
    [Input('depth_2', 'hoverData'), Input('depth', 'clickData'),
     Input('signal_data_filtered', 'children'),
     Input('date_picker', 'date'), Input('msuk_selector', 'value'), Input('use_cache', 'children'),
     Input('hour_slider', 'value'), Input('minute_slider', 'value'),
     Input('second_slider', 'value'), Input('micros_slider', 'value')])
def display_click_data(click_data_2, click_data_1, *args):
    """
    Generates trade_volume_details figure on clicking the depth figures.
    Separate from main figure updater because of click & hover data inputs
    """
    ctx = dash.callback_context
    df = get_filtered_data(*args)
    fig = FigureGenerator.trade_volume_detail(ctx, df)
    return fig


@app.callback(
    Output('output_timeframe', 'children'),
    [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
     Input('second_slider', 'value'), Input('micros_slider', 'value'),
     Input('date_picker', 'date')])
@cache.memoize(timeout=20)
def generate_output_timeframe(hour_value, minute_value, second_value, micros_value, date):
    """
    Callback to display selected timeframe
    """
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


@click.command()
@click.option("--use-cache/--no-cache", "-c", is_flag=True, default=True,
              help="Use cache for data loading. Recommended for large datasets.")
@click.option("--debug/--no-debug", "-d", is_flag=True, default=True,
              help="Run dash app in debug mode.")
def main(use_cache, debug):
    """
    Runs a server for displaying book data on a webpage.
    """

    app.layout = generate_app_layout(FEATURES, DATA_FILES, use_cache)
    if debug:
        app.logger.setLevel(logging.INFO)

    app.logger.info(f" * Data caching: {'on' if use_cache else 'off'}")
    app.run_server(debug=debug)


if __name__ == '__main__':
    main()

