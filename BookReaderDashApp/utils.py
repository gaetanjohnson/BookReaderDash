import pandas as pd
import dash_html_components as html
import numpy as np
import csv
import dash_core_components as dcc
import dash_daq as daq


def create_more_date(number):
    volumes = np.round(np.random.binomial(200, 0.5, 2 * number), 1)
    start_nanos_epoch = 1565157926599450000
    periods = start_nanos_epoch + np.cumsum(np.random.binomial(1000, 0.5, number) * 1000)
    datetimes = pd.to_datetime(periods)
    msuk, source, tradePx, tradeSz, channelId, seqNum, msgIdx = 79889147, 'EUREX', 0, 0, 0, 597283, 0
    prices_bid = create_prices(number)
    prices_ask = prices_bid + np.round(np.random.gamma(0.2, 0.1, size=number), 2)
    data = []
    for i in range(number):
        line = [periods[i], datetimes[i], msuk, source,
                prices_bid[i], volumes[2 * i], prices_ask[i], volumes[2 * i + 1],
                prices_bid[i], volumes[2 * i], prices_ask[i], volumes[2 * i + 1],
                tradePx, tradeSz, channelId, seqNum, msgIdx]
        data.append(line)
    return data


def create_prices(number):
    percent_changes = np.random.normal(0.0001, 0.01, number)
    prices = 82.2 * np.exp(np.cumsum(percent_changes))
    return np.round(prices, 3)


def save_data(data):
    with open('data/data_book_big.csv', mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in data:
            writer.writerow(line)


def generate_slider(id_cl, id_rs, min, max, step, value, marks_delta, symbol):
    marks = {i: {'label': f'{int(i/100000)}e5{symbol}', 'style': {'font-size': '8px'}}
             for i in range(min, max+marks_delta, marks_delta)} if symbol=='ms' \
        else {i: f'{i}{symbol}' for i in range(min, max+marks_delta, marks_delta)}

    slider = html.Div([
            daq.BooleanSwitch(
                id=id_cl,
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
# data = create_more_date(1000)
# save_data(data)
