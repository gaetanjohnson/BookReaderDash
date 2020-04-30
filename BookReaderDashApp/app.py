import dash
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from utils import generate_table, import_and_format
import dash_table
import re

columns_to_display = ['bidSz','bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = import_and_format('./data_book.csv')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Book Reader'),
    dcc.DatePickerSingle(
        id='date_picker',
        min_date_allowed=dt(2010, 8, 5),
        max_date_allowed=dt.today(),
        initial_visible_month=dt.today(),
        date=str(dt.today())
    ),
    dcc.RangeSlider(
        id='hour_slider',
        min=0,
        max=24,
        step=1,
        value=[8, 18],
        marks={i: f'{i}h' for i in range(0, 24, 3)}
    ),
    dcc.RangeSlider(
        id='minute_slider',
        min=0,
        max=60,
        step=0.5,
        value=[5, 15],
        marks={i: f'{i}min' for i in range(0, 60, 10)}
    ),
    dcc.RangeSlider(
        id='second_slider',
        min=0,
        max=60,
        step=0.5,
        value=[5, 15],
        marks={i: f'{i}s' for i in range(0, 60, 10)}
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in columns_to_display],
    ),
])

@app.callback(Output('table', 'data'),
    [Input('hour_slider', 'value'), Input('minute_slider', 'value'),
     Input('second_slider', 'value'), Input('date_picker', 'date')])
def update_figure(hour_value, minute_value, second_value, date):
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
    df_to_display = filtered_df[columns_to_display].to_dict('records')
    return df_to_display


if __name__ == '__main__':
    app.run_server(debug=True)