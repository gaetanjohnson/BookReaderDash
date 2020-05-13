import abc
import pandas as pd


class DataReader(abc.ABC):
    """
    Abstract data reader class. All subclasses must implement a `load` class method.
    """

    # required columns for the data after the .load of the subclasses.
    _required_columns = ("nanosEpoch", "bidPx", "bidSz", "askPx", "askSz", "tradePx", "tradeSz", "direction", "spread",
                         "cumulative_trade_volume", "size_imbalance")

    @classmethod
    @abc.abstractmethod
    def load(cls, path):
        """
        Load data.

        Parameters
        ----------
        path : pathlib.Path or str
            path or path-like object pointing to the data file.

        Returns
        -------
        pandas.DataFrame
            A dataframe of entries containing the required columns.
        """
        pass

    @staticmethod
    def serialize(df, path):
        """
        Serialize to disk after validating the format.

        Parameters
        ----------
        df : pandas.DataFrame
            A dataframe of entries containing the required columns.

        path : pathlib.Path or str
            path or path-like object pointing to where the data will be serialized.
        """
        DataReader._validate(df)
        pd.to_pickle(df, path)

    @staticmethod
    def deserialize(path):
        """
        De-serialize data committed to disk using .serialize

        Parameters
        ----------
        path : pathlib.Path or str
            path or path-like object pointing to the serialized data.

        Returns
        -------
        pandas.DataFrame
            A dataframe of entries containing the required columns.
        """
        df = pd.read_pickle(path)
        DataReader._validate(df)
        return pd.read_pickle(path)

    @staticmethod
    def _validate(df):
        """
        Validate data.

        Parameters
        ----------
        df : pandas.DataFrame
            A dataframe of entries containing the required columns.

        Raises
        ------
        RuntimeError
            In case one of the required columns is missing in the dataframe.
        """
        # fixme do we validate dtypes too?
        if any(c not in df.columns for c in DataReader._required_columns):
            raise RuntimeError(f"Non conforming. Missing required columns (one of {DataReader._required_columns}).")

