import pandas as pd
from dataclasses import TopBook
import dash_html_components as html


def import_and_format(datafile):
    data = pd.read_csv(datafile)
    data.drop(columns=['channelId'], inplace=True)
    data['time'] = pd.to_datetime(data['time'])
    data['date'] = data['time'].dt.date
    # data['time'] = data['time'].dt.time
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
