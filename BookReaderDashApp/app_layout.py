from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html

from utils import generate_slider, generate_datatable


def generate_app_layout(features, files, use_cache):
    app_layout = html.Div([
        html.Div([
            html.Div(id='use_cache', children=[use_cache],style={'display': 'none'}),
            html.Div(id='signal_data_ready', style={'display': 'none'}),
            html.Div(id='filtered_df', style={'display': 'none'}),
            html.Div(
                html.H3('Book Reader'),
                className='title',
                style={'textAlign': 'center'}),
            html.Hr(),
            dcc.Dropdown(
                id='msuk_selector',
                options=[],
                value=None,
            ),
            html.Hr(),
            dcc.Dropdown(
                id='file',
                options=[{'label': file, 'value': file} for file in files],
                value=files[0],
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
                    persistence=True,
                    style={'width': '70%'}
                )],
                className='row'
            ),
            # TODO Clean hard coded values below
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
                            dcc.Graph(id='bid_ask'),
                            dcc.Graph(id='size_imbalance')
                        ]),
                dcc.Tab(label='Depth Analysis',
                        children=[
                            html.Div(children=[
                                dcc.Graph(id='depth_2', className='depthgraph'),
                                dcc.Slider(id='color_scale', min=1, max=10, step=0.5, value=2, vertical=True,
                                           className='colorslider', verticalHeight=200, marks={1: 'Linear', 10: 'Log'}),
                            ],
                            className='row rowgraph'),
                            dcc.Graph(id='depth_detail'),
                            dcc.Graph(id='depth')
                        ])
            ]),
            generate_datatable('table'),
            ],
        className='eight columns')
    ],
    className='row flex-display')
    return app_layout