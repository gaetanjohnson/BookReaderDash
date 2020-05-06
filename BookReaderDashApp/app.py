import re
from datetime import datetime as dt

import dash
from dash.dependencies import Input, Output

import plotly.express as px

from app_layout import generate_app_layout

from models import BookReader, TopBookReader

# TODO: Handle Data (with SQL database ?)
# TODO: Handle the 2nd form of data
# TODO: Change layout style
# TODO: Choose what and how to display

columns_to_display = ['time', 'date', 'bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz', 'direction']
# names_to_display = ['Time', 'Volume (Bid)', 'Bid', 'Ask', 'Volume (Ask)', 'Trade Price', 'Trade Volume']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = TopBookReader.load("data/data_book_big.csv")
# df = BookReader.load("data/new_data.txt")

df['time_readable'] = df['nanosEpoch'] - 1565157926599450000

features = [
    {"label": "Trade Price", "value": "tradePx"},
    {"label": "Trade Size", "value": "tradeSz"},
    {"label": "Bid Size", "value": "bidSz"},
    {"label": "Bid Price", "value": "bidPx"},
    {"label": "Ask Size", "value": "askSz"},
    {"label": "Ask Price", "value": "askPx"},
    {"label": "Spread", "value": "spread"},
]

msuks = df['msuk'].unique()

app = dash.Dash(__name__)

app.layout = generate_app_layout(msuks, features)


@app.callback([Output('table', 'data'), Output('time_series', 'figure')],
              [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value'),
               Input('date_picker', 'date'), Input('msuk_selector', 'value'),
               Input('feature_selector', 'value')])
def update_figure(hour_value, minute_value, second_value, micros_value, date, msuk, feature):
    filtered_df = df.copy()
    if date is not None:
        date = dt.strptime(re.split(r"T| ", date)[0], '%Y-%m-%d')
        date = dt.date(date)
        filtered_df = filtered_df[(filtered_df.date == date)]
    if hour_value is not None:
        min_hour, max_hour = hour_value
        filtered_df = filtered_df[(filtered_df.hour <= max_hour) & (filtered_df.hour >= min_hour)]
    if minute_value is not None:
        min_minute, max_minute = minute_value
        filtered_df = filtered_df[(filtered_df.minute <= max_minute) & (filtered_df.minute >= min_minute)]
    if second_value is not None:
        min_second, max_second = second_value
        filtered_df = filtered_df[(filtered_df.second <= max_second) & (filtered_df.second >= min_second)]
    if micros_value is not None:
        min_micros, max_micros = micros_value
        filtered_df = filtered_df[(filtered_df.microsecond <= max_micros) & (filtered_df.microsecond >= min_micros)]
    if msuk is not None:
        filtered_df = filtered_df[(filtered_df.msuk == msuk)]
    df_to_display = filtered_df[columns_to_display].to_dict('records')
    figure = generate_figure(filtered_df, feature)
    return df_to_display, figure


def generate_figure(df, feature):
    fig = px.line(df, x="time_readable", y=feature)
    fig.update_xaxes(rangeslider_visible=False)
    return fig


@app.callback(
    Output('output_timeframe', 'children'),
    [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
     Input('second_slider', 'value'), Input('micros_slider', 'value'),
     Input('date_picker', 'date')])
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
