import dash_core_components as dcc
import dash_html_components as html
import dash_table
from utils import generate_slider
from datetime import datetime as dt

def generate_app_layout(fig):
    app_layout = html.Div([
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
                    html.Div(id='output_timeframe'),
                    generate_slider('all_hour', 'hour_slider', 0, 24, 1, [6, 10], 3, 'h'),
                    generate_slider('all_min', 'minute_slider', 0, 60, 1, [4, 10], 10, 'mn'),
                    generate_slider('all_second', 'second_slider', 0, 60, 1, [5, 30], 10, 's'),
                    generate_slider('all_micros', 'micros_slider', 0, 1000000, 10, [597045, 650000], 100000, 'ms')
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
            columns=[{'name': ['DateTime', 'Date'], 'id': 'date'},
                     {'name': ['DateTime', 'Time'], 'id': 'time'},
                     {"name": ["Bid", "Volume"], "id": 'bidSz'},
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
    return app_layout