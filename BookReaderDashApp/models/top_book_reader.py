import pandas as pd

from .base import DataReader


class TopBookReader(DataReader):
    size_to_unit = {10: 's', 13: 'ms', 16: 'us', 19: 'ns'}

    @classmethod
    def load(cls, path):
        df = pd.read_csv(path)
        return cls.standardize_df(df)

    @classmethod
    def standardize_df(cls, df, inplace=False):
        if not inplace:
            # no support for cases where deep copy ans shallow copy are different yet
            df = df.copy()

        # We have to manually determine the unit of the timestamp, because it is not done properly by pandas
        unit = cls.size_to_unit[len(str(df["nanosEpoch"][0]))]

        df.drop(columns=["channelId"], inplace=True)
        df["datetime"] = pd.to_datetime(df["nanosEpoch"], unit=unit)
        df["date"] = df["datetime"].dt.date
        df["hour"] = df["datetime"].dt.hour
        df["minute"] = df["datetime"].dt.minute
        df["second"] = df["datetime"].dt.second
        df["microsecond"] = df["datetime"].dt.microsecond
        df["time"] = df["datetime"].dt.time

        # No direction because it is the top of the book (does not represent a trade)
        df["direction"] = ""

        df["spread"] = df["askPx"] - df["bidPx"]

        if not inplace:
            return df