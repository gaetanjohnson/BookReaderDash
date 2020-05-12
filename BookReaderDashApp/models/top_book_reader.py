import pandas as pd

from .base import DataReader


class TopBookReader(DataReader):
    _size_to_unit = {10: 's', 13: 'ms', 16: 'us', 19: 'ns'}
    _required_entries = ['nanosEpoch', 'time', 'msuk', 'source', 'cbidPx', 'cbidSz', 'caskPx', 'caskSz',
                         'bidPx', 'bidSz', 'askPx', 'askSz', 'tradePx', 'tradeSz', 'channelId', 'seqNum', 'msgIdx']

    @classmethod
    def load(cls, path):
        df = pd.read_csv(path)
        cls._check_file(df.columns)
        return cls.standardize_df(df)

    @classmethod
    def _check_file(cls, columns):
        if any(c not in columns for c in TopBookReader._required_entries):
            raise RuntimeError(f"Non conforming. File is missing required columns (one of {TopBookReader._required_entries}).")

    @classmethod
    def standardize_df(cls, df, inplace=False):
        if not inplace:
            # no support for cases where deep copy ans shallow copy are different yet
            df = df.copy()

        # We have to manually determine the unit of the timestamp, because it is not done properly by pandas
        unit = cls._size_to_unit[len(str(df["nanosEpoch"][0]))]

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
        # TODO: find a better way
        df['cumulative_trade_volume'] = df['askSz']
        df['size_imbalance'] = df['askSz'] - df['bidSz']
        if not inplace:
            return df
