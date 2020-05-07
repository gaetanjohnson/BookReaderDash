import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from models import BookReader, TopBookReader
import os
from pathlib import Path


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
                className='sliderslider'),
    ],
        className='row'
    )


    return slider

def load_data(file):
    filename, file_extension = os.path.splitext(file)
    pkl_path = Path('cache/pickle/' + filename + '.pkl')
    pickle_exists = pkl_path.exists()

    if file_extension not in ['.data', '.csv']:
        raise TypeError('File supported are .csv or .data')

    if file_extension == '.data':
        reader = BookReader()
    else:
        reader = TopBookReader()

    if not pickle_exists:
        df = reader.load('data/' + file)
        reader.serialize(df, pkl_path)
    else:
        df = reader.deserialize(pkl_path)
    return df