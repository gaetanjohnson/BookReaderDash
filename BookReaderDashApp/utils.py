import pandas as pd
from dataclasses import TopBook
import dash_html_components as html
import random
import numpy as np
import csv



def import_and_format(datafile):
    data = pd.read_csv(datafile)
    data.drop(columns=['channelId'], inplace=True)
    data['time'] = pd.to_datetime(data['nanosEpoch'])
    data['date'] = data['time'].dt.date
    data['hour'] = data['time'].dt.hour
    data['minute'] = data['time'].dt.minute
    data['second'] = data['time'].dt.second
    data['microsecond'] = data['time'].dt.microsecond
    data['nanosecond'] = data['time'].dt.nanosecond
    return data

def read_entries_file(datafile):
    lines = []
    with open(datafile, 'r') as f:
        for line in f:
            lines.append(line)
    return lines

# def parse_and_format(lines):

def save_to_database(datafile):
    data = import_and_format(datafile).to_dict('records')
    for entry in data:
        new_entry = TopBook(**entry)


def create_more_date(number):
    volumes = np.round(np.random.binomial(200, 0.5, 2 * number), 1)
    start_nanos_epoch = 1565157926599450000
    periods = start_nanos_epoch + np.cumsum(np.random.binomial(1000, 0.5, number) * 1000)
    datetimes = pd.to_datetime(periods)
    msuk, source, tradePx,tradeSz, channelId, seqNum, msgIdx = 79889147, 'EUREX', 0, 0, 0, 597283, 0
    prices_bid = create_prices(number)
    prices_ask = prices_bid + np.round(np.random.gamma(0.2, 0.1, size=number), 2)
    data = []
    for i in range(number):
        line = [periods[i], datetimes[i], msuk, source,
                prices_bid[i], volumes[2*i], prices_ask[i], volumes[2*i+1],
                prices_bid[i], volumes[2 * i], prices_ask[i], volumes[2 * i + 1],
                tradePx, tradeSz, channelId, seqNum, msgIdx]
        data.append(line)
    return data


def create_prices(number):
    percent_changes = np.random.normal(0.0001, 0.01, number)
    prices = 82.2 * np.exp(np.cumsum(percent_changes))
    return np.round(prices, 3)

def save_data(data):
    with open('data_book_big.csv', mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in data:
            writer.writerow(line)

# data = create_more_date(1000)
# save_data(data)