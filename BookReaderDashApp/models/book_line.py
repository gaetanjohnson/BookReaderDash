import pandas as pd

from .base import DataReader


class BookLineReader(DataReader):

    @classmethod
    def load(cls, path):
        df = pd.read_csv(path)
        return cls.standardize_df(df)

    @classmethod
    def standardize_df(cls, df, inplace=False):
        if not inplace:
            # no support for cases where deep copy ans shallow copy are different yet
            df = df.copy()

        df.drop(columns=['channelId'], inplace=True)
        df['datetime'] = pd.to_datetime(df['nanosEpoch'])
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        df['minute'] = df['datetime'].dt.minute
        df['second'] = df['datetime'].dt.second
        df['microsecond'] = df['datetime'].dt.microsecond
        df['time'] = df['datetime'].dt.time

        if not inplace:
            return df
