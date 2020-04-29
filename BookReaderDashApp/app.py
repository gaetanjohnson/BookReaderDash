import dash
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from utils import generate_table, import_and_format

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = import_and_format('./data_book.csv')
min_time = df['nanosEpoch'].min()
max_time = df['nanosEpoch'].max()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

@app.callback(
    Output('table', 'children'),
    [Input('date_slider', 'value'),
     Input('date_picker', 'date')])
def update_figure(value, date):
    min_time, max_time = value
    print(df)
    filtered_df = df[(df.date == date)]
    print(filtered_df)
    return generate_table(filtered_df)


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
    # dcc.RangeSlider(
    #     id='date_slider',
    #     min=min_time,
    #     max=max_time,
    #     step=None,
    #     value=[min_time, max_time]
    # ),
    html.Div(id='table')
])


if __name__ == '__main__':
    app.run_server(debug=True)