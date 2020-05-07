import abc
import pandas as pd


class DataReader(abc.ABC):
    """
    Abstract data reader class. All subclasses must implement a `load` class method.
    todo start using pandas style docstrings for documentation
    """

    _required_columns = ("nanosEpoch", "bidPx", "bidSz", "askPx", "askSz", "tradePx", "tradeSz", "direction", "spread")

    @classmethod
    @abc.abstractmethod
    def load(cls, path):
        """
        Load data from custom format.
        Returns pd.DataFrame containing all required columns as specified above
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
        return pd.read_pickle(path)

    @staticmethod
    def _validate(df):
        # fixme do we validate dtypes too?
        if any(c not in df.columns for c in DataReader._required_columns):
            raise RuntimeError(f"Non conforming. Missing required columns (one of {DataReader._required_columns}).")

