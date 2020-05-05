import abc

import pandas as pd


class DataReader(abc.ABC):

    _required_columns = ("nanosEpoch", "bidPx", "bidSz", "askPx", "askSz", "tradePx", "tradeSz")

    @classmethod
    @abc.abstractmethod
    def load(cls, path):
        """
        Load data from custom format.
        """
        pass

    @staticmethod
    def serialize(df, path):
        """
        Commit the data to disk assuming it follows the norm
        """
        DataReader._validate(df)
        pd.to_pickle(df, path)

    @staticmethod
    def deserialize(path):
        """
        Read the data from disk assuming it follows the norm
        """
        df = pd.read_pickle(path)
        DataReader._validate(df)
        return pd.read_csv(path)

    @staticmethod
    def _validate(df):
        if any(c not in df.columns for c in DataReader._required_columns):
            raise RuntimeError(f"Non conforming. Missing required columns (one of {DataReader._required_columns}).")

