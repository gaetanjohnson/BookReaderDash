import pandas as pd
from dataclasses import BestBookLevel
import dash_html_components as html


def import_and_format(datafile):
    data = pd.read_csv(datafile)
    data.drop(columns=['channelId'], inplace=True)
    data['time'] = pd.to_datetime(df['nosEpoch'])
    data['date'] = data['time'].dt.date
    data['hour'] = data['time'].dt.hour
    data['minute'] = data['time'].dt.minute
    data['second'] = data['time'].dt.second
    data['microsecond'] = data['time'].dt.microsecond
    data['nanosecond'] = data['time'].dt.nanosecond
    return data

def save_to_database(datafile):
    data = import_and_format(datafile).to_dict('records')
    for entry in data:
        new_entry = BestBookLevel(**entry)


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])
