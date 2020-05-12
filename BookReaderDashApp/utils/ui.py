import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq


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

def generate_colors(scale):
    colorscale= [
        [0, '#f0f921'],
        [1./(scale**8), '#fdca26'],
        [1./(scale**7), '#fb9f3a'],
        [1./(scale**6), '#ed7953'],
        [1./(scale**5), '#d8576b'],
        [1./(scale**3), '#9c179e'],
        [1./(scale**2), '#7201a8'],
        [1./(scale**1), '#46039f'],
        [1., '#0d0887'],
    ]
    return colorscale
