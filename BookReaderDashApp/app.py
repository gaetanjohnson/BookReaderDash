import re
from datetime import datetime as dt

import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from utils import import_and_format

columns_to_display = ['bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz']
names_to_display = ['Volume (Bid)', 'Bid', 'Ask', 'Volume (Ask)', 'Trade Price', 'Trade Volume']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = import_and_format('./data_book.csv')

fig = px.line(df, x="time", y="bidPx", title="Bid")
fig.update_xaxes(rangeslider_visible=True)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(figure=fig),
    html.Div(
        html.H1(children='Book Reader'),
        style={'display': 'flex', 'margin': 0, 'position': 'fixed', 'right': 0, 'top': 0, 'left': 0,
               'padding': 0, 'font-size': 0, 'background-color': '#f6f6f6', 'border-bottom': '1px solid #cccccc',
               'text-align': 'center'}
    ),
    html.Div([
        html.Div(
            dcc.DatePickerSingle(
                id='date_picker',
                min_date_allowed=dt(2010, 8, 5),
                max_date_allowed=dt.today(),
                initial_visible_month=dt(2019, 8, 7),
                date=str(dt(2019, 8, 7))
            ),
            style={'width': '30%', 'float': 'left', 'display': 'inline-block'}
        ),
        html.Div(
            children=[
                html.Div([
                    dcc.Checklist(id='all_hour',
                                  options=[{'label': 'All', 'value': 'all_hour'}]),
                    dcc.RangeSlider(
                        id='hour_slider',
                        min=0,
                        max=24,
                        step=1,
                        value=[6, 10],
                        marks={i: f'{i}h' for i in range(0, 24, 3)}
                    )],
                ),
                html.Div([
                    dcc.Checklist(id='all_min',
                                  options=[{'label': 'All', 'value': 'all_min'}]),
                    dcc.RangeSlider(
                        id='minute_slider',
                        min=0,
                        max=60,
                        step=0.5,
                        value=[4, 10],
                        marks={i: f'{i}min' for i in range(0, 60, 10)}
                    )],
                ),
                html.Div([
                    dcc.Checklist(id='all_second',
                                  options=[{'label': 'All', 'value': 'all_second'}, ]),
                    dcc.RangeSlider(
                        id='second_slider',
                        min=0,
                        max=60,
                        step=0.5,
                        value=[5, 30],
                        marks={i: f'{i}s' for i in range(0, 60, 10)}
                    )],
                )
                ],
            style={'width': '60%',  # 'float': 'right',
                   'display': 'flex',
                   'flex-direction': 'column'
                   }
        )],
        style={'justify-content': 'space-between', 'display': 'flex', 'margin-top': '100px'}
    ),

    dash_table.DataTable(
        id='table',
        columns=[{"name": ["Bid", "Volume"], "id": 'bidSz'},
                 {"name": ["Bid", "Price"], "id": 'bidPx'},
                 {"name": ["Ask", "Price"], "id": 'askPx'},
                 {"name": ["Ask", "Volume"], "id": 'askSz'},
                 {"name": ["Trade", "Price"], "id": 'tradePx'},
                 {"name": ["Trade", "Volume"], "id": 'tradeSz'}],
# {"name": i, "id": j} for (i,j) in zip(names_to_display, columns_to_display)],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }],
        style_cell={
                'textAlign': 'center'
            },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        merge_duplicate_headers=True
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


if __name__ == '__main__':
    app.run_server(debug=True)
