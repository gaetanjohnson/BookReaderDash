from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_table

from utils import generate_slider


def generate_app_layout(msuks, features):
    app_layout = html.Div([
        html.Div([
            html.Div(
                html.H3('Book Reader'),
                className='title',
                style={'textAlign': 'center'}),
            html.Hr(),
            dcc.Dropdown(
                id='msuk_selector',
                options=[{'label': msuk, 'value': msuk} for msuk in msuks],
                value=msuks[0],
            ),
            html.Hr(),
            html.Div([
                html.Div('Date to display: ',
                         style={'width': '30%', 'margin': 'auto'}),
                dcc.DatePickerSingle(
                    id='date_picker',
                    min_date_allowed=dt(2010, 8, 5),
                    max_date_allowed=dt.today(),
                    initial_visible_month=dt(2019, 8, 7),
                    date=str(dt(2019, 8, 7)),
                    style={'width': '70%'}
                )],
                className='row'
            ),
            html.Div(
                children=[
                    generate_slider('all_hour', 'hour_slider', 0, 24, 1, [6, 10], 3, 'h'),
                    generate_slider('all_min', 'minute_slider', 0, 60, 1, [4, 10], 10, 'mn'),
                    generate_slider('all_second', 'second_slider', 0, 60, 1, [5, 30], 10, 's'),
                    generate_slider('all_micros', 'micros_slider', 0, 1000000, 10, [597045, 650000], 100000, 'ms')
                    ],
            ),
            html.Div(id='output_timeframe'),
            ],
            style={'justify-content': 'space-between', 'margin-top': 0},
            className='four columns sidebar'
        ),

        html.Div([
            dcc.Tabs([
                dcc.Tab(label='Time Series',
                        children=[
                            dcc.Dropdown(
                                id='feature_selector',
                                options=features,
                                value=features[0]["value"],
                            ),
                            dcc.Graph(id='time_series'),
                            dcc.Graph(id='bid_ask')
                        ]),
                dcc.Tab(label='Depth Analysis',
                        children=['TODO'])
            ]),
            dash_table.DataTable(
                id='table',
                columns=[{'name': ['DateTime', 'Date'], 'id': 'date'},
                         {'name': ['DateTime', 'Time'], 'id': 'time'},
                         {'name': ['Bid', 'Volume'], 'id': 'bidSz'},
                         {'name': ['Bid', 'Price'], 'id': 'bidPx'},
                         {'name': ['Ask', 'Price'], 'id': 'askPx'},
                         {'name': ['Ask', 'Volume'], 'id': 'askSz'},
                         {'name': ['Trade', 'Price'], 'id': 'tradePx'},
                         {'name': ['Trade', 'Volume'], 'id': 'tradeSz'},
                         {'name': ['Trade', 'Direction'], 'id': 'direction'}],
                # TODO CLean the style below
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }] + [
                    {
                        'if': {'column_id': c},
                        'borderLeft': '1px solid #506783'
                    } for c in ['date', 'bidSz', 'tradePx']] + [
                    {
                    'if': {'column_id': 'direction'},
                    'borderRight': '1px solid #506783'}
                ],

                style_cell={
                        'textAlign': 'center'
                    },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'border': '1px solid #506783'
                },
                merge_duplicate_headers=True
            ),
            ],
        className='eight columns')
    ],
    className='row flex-display')
    return app_layout