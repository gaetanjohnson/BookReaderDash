import re

import pandas as pd

from .base import DataReader


class BookReader(DataReader):
    """
    DataReader for book line data.
    """

    # We compile the regexes ahead of time for performance.
    _compiled_regexes = {
        "msuk": re.compile(r"\w+\((\d+)\)"),
        "datetime": re.compile(r"our=(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?) (?:\w+) flags="),
        "trade": re.compile(r"(?:Buy|Sell) ([^\s]+)@([^\s]+)"),
        "direction" : re.compile(r"Buy|Sell"),
        "bid": re.compile(r"bid:([^\s]+)@([^\s]+)"),
        "cbid": re.compile(r"cbid:([^\s]+)@([^\s]+)"),
        "ask": re.compile(r"ask:([^\s]+)@([^\s]+)"),
        "cask": re.compile(r"cask:([^\s]+)@([^\s]+)"),
    }

    @classmethod
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

        Raises
        ------
        RuntimeError
            In case a parse operation is unsuccessful.
        """
        with open(path, mode="r") as f:
            lines = f.readlines()

        # generator expression, (lazily) use once and throw away
        data = (cls._parse_entry(line, number) for number, line in enumerate(lines, 1))

        # let pandas do the type conversions
        df = pd.DataFrame(data).astype({
            "msuk": "int64",
            "datetime": "datetime64[ns]",
            "tradeSz": "int64",
            "bidSz": "int64",
            "askSz": "int64",
            "cbidSz": "int64",
            "caskSz": "int64",
            "tradePx": "float64",
            "bidPx": "float64",
            "askPx": "float64",
            "cbidPx": "float64",
            "caskPx": "float64",
            "direction": "str",
            "spread": 'float64'
        })

        # compute remaining required columns
        df["nanosEpoch"] = df["datetime"].values.astype("int64")
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        df['minute'] = df['datetime'].dt.minute
        df['second'] = df['datetime'].dt.second
        df['microsecond'] = df['datetime'].dt.microsecond
        df['time'] = df['datetime'].dt.time
        df['cumulative_trade_volume'] = df.groupby(['nanosEpoch', 'direction'])['tradeSz'].cumsum()
        # TODO: comoute size imbalances for different levels
        df['size_imbalance'] = df['askSz'] - df['bidSz']

        return df

    @classmethod
    def _parse_entry(cls, line, line_number):
        """
        Parse one data entry.

        Parameters
        ----------
        line : str
            data entry.

        line_number : int
            line number of the data entry.

        Returns
        -------
        dict
            from str to str, representing the attributes of the data entry.

        Raises
        ------
        RuntimeError
            In case a parse operation is unsuccessful.
        """
        data_dict = {}

        # parsing msuk
        match = cls._unsafe_search(line, line_number, "msuk")
        data_dict["msuk"] = match.group(1)

        # parsing datetime
        match = cls._unsafe_search(line, line_number, "datetime")
        data_dict["datetime"] = match.group(1)

        # parsing trade direction
        match = cls._unsafe_search(line, line_number, "direction")
        data_dict["direction"] = match.group(0)

        # parsing price and trade data
        for attr in ("trade", "bid", "cbid", "ask", "cask"):
            match = cls._unsafe_search(line, line_number, attr)
            size, price = match.group(1), match.group(2)
            data_dict[attr + "Sz"] = size
            data_dict[attr + "Px"] = float(price)

        data_dict['spread'] = data_dict['askPx'] - data_dict['bidPx']

        return data_dict

    @classmethod
    def _unsafe_search(cls, line, line_number, attr):
        """
        Use regex to get a regex match object for an attribute, raises an exception on fail.

        Parameters
        ----------
        line : str
            data entry.

        line_number : int
            line number of the data entry.

        attr : str
            the attribute to parse.

        Returns
        -------
        regex match group

        Raises
        ------
        RuntimeError
            In case the regex doesn't match.
        """
        match_result = cls._compiled_regexes[attr].search(line)
        if match_result is None:
            raise RuntimeError(f"Failed parsing attribute `{attr}` on line number `{line_number}`.")
        return match_result
