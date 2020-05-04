import re
from datetime import datetime as dt

import plotly.express as px
import plotly.graph_objects as go

import dash
from dash.dependencies import Input, Output

from app_layout import generate_app_layout
from utils import import_and_format, generate_slider

columns_to_display = ['time', 'date', 'bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz']
# names_to_display = ['Time', 'Volume (Bid)', 'Bid', 'Ask', 'Volume (Ask)', 'Trade Price', 'Trade Volume']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = import_and_format('./data_book_big.csv')

df['time_readable'] = df['nanosEpoch'] - 1565157926599450000
fig = px.line(df, x="time_readable", y="bidPx", title="Bid")
fig.update_xaxes(rangeslider_visible=True)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = generate_app_layout(fig)


@app.callback(Output('table', 'data'),
              [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
               Input('second_slider', 'value'), Input('micros_slider', 'value'),
               Input('date_picker', 'date')])
def update_figure(hour_value, minute_value, second_value, micros_value, date):
    filtered_df = df.copy()
    if date is not None:
        date = dt.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
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
        print(min_micros, max_micros)
        filtered_df = filtered_df[(filtered_df.microsecond <= max_micros) & (filtered_df.microsecond >= min_micros)]
    df_to_display = filtered_df[columns_to_display].to_dict('records')
    return df_to_display

@app.callback(
    Output('output_timeframe', 'children'),
    [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
     Input('second_slider', 'value'), Input('micros_slider', 'value'),
     Input('date_picker', 'date')])
def generate_output_timeframe(hour_value, minute_value, second_value, micros_value, date):
    return f'Selected Timeframe: {date.split()[0]} {hour_value}h {minute_value}min {second_value}s {micros_value}ms'


@app.callback(
    Output('hour_slider', 'value'),
    [Input('all_hour', 'value')])
def set_hour_values(value):
    return [0, 24] if value else [6, 10]


@app.callback(
    Output('minute_slider', 'value'),
    [Input('all_min', 'value')])
def set_hour_values(value):
    return [0, 60] if value else [4, 10]


@app.callback(
    Output('second_slider', 'value'),
    [Input('all_second', 'value')])
def set_hour_values(value):
    return [0, 60] if value else [5, 30]

@app.callback(
    Output('micros_slider', 'value'),
    [Input('all_micros', 'value')])
def set_micros_values(value):
    return [0, 1000000] if value else [597045, 650000]

if __name__ == '__main__':
    app.run_server(debug=True)
