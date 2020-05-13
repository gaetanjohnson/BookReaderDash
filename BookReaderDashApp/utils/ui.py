import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table

COLUMNS_DATATABLE = [{'name': ['DateTime', 'Date'], 'id': 'date'},
                         {'name': ['DateTime', 'Time'], 'id': 'time'},
                         {'name': ['Bid', 'Volume'], 'id': 'bidSz'},
                         {'name': ['Bid', 'Price'], 'id': 'bidPx'},
                         {'name': ['Ask', 'Price'], 'id': 'askPx'},
                         {'name': ['Ask', 'Volume'], 'id': 'askSz'},
                         {'name': ['Trade', 'Price'], 'id': 'tradePx'},
                         {'name': ['Trade', 'Volume'], 'id': 'tradeSz'},
                         {'name': ['Trade', 'Direction'], 'id': 'direction'}]

def generate_slider(id_bs, id_rs, min, max, step, value, marks_delta, symbol):
    marks = {i: {'label': f'{int(i/100000)}e5{symbol}', 'style': {'font-size': '8px'}}
             for i in range(min, max+marks_delta, marks_delta)} if symbol=='ms' \
        else {i: f'{i}{symbol}' for i in range(min, max+marks_delta, marks_delta)}

    slider = html.Div([
        daq.BooleanSwitch(
            id=id_bs,
            on=False,
            label={'label': 'All', 'style': {'fontSize': '10%'}},
            className='sliderbutton',
        ),
        dcc.RangeSlider(
            id=id_rs,
            min=min,
            max=max,
            step=step,
            value=value,
            marks=marks,
            tooltip={'always_visible': False},
            className='sliderslider',
            persistence=True),
    ],
        className='row'
    )


    return slider

def generate_datatable(id):
    table = dash_table.DataTable(
            id=id,
            columns=COLUMNS_DATATABLE,
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
        )
    return table


def generate_colors(scale):
    colors = ['#f0f921', '#fdca26', '#fb9f3a', '#ed7953', '#d8576b', '#9c179e', '#7201a8', '#46039f', '#0d0887']
    colorscale = [[0, colors[0]]]
    if scale == 1:
        colorscale += [[i*1/8, colors[i]] for i in range(1,8)]
    else:
        colorscale += [[1/(scale**(8-i)), colors[i]] for i in range(1, 8)]
    colorscale += [[1, colors[-1]]]
    return colorscale
