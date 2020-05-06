import re

import pandas as pd

from .base import DataReader


class BookReader(DataReader):
    # fixme timezone info is intentionally left off to avoid pandas warnings
    # fixme the data format includes two dates: 'our', 'source', which one to choose?
    # todo write some unittests
    # todo generate random data in this format
    # compile regex ahead of time
    _compiled_regexes = {
        "msuk": re.compile(r"\w+\((\d+)\)"),
        "datetime": re.compile(r"our=(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?) (?:\w+) flags="),
        "trade": re.compile(r"(?:Buy|Sell) ([^\s]+)@([^\s]+)"),
        "direction" : re.compile(r"Buy|Sell"),
        "bid": re.compile(r"bid:([^\s]+)@([^\s]+)"),
        "cbid": re.compile(r"cbid:([^\s]+)@([^\s]+)"),
        "ask": re.compile(r"ask:([^\s]+)@([^\s]+)"),
        "cask": re.compile(r"cask:([^\s]+)@([^\s]+)"),
    }

    @classmethod
    def load(cls, path):
        with open(path, mode="r") as f:
            lines = f.readlines()

        # generator expression, use once and throw away
        data = (cls._parse_entry(line, number) for number, line in enumerate(lines, 1))

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
            "direction": "string",
        })

        df["nanosEpoch"] = df["datetime"].values.astype("int64")
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        df['minute'] = df['datetime'].dt.minute
        df['second'] = df['datetime'].dt.second
        df['microsecond'] = df['datetime'].dt.microsecond
        df['time'] = df['datetime'].dt.time

        return df

    @classmethod
    def _parse_entry(cls, line, line_number):
        data_dict = {}

        # parsing msuk
        match = cls._unsafe_search(line, line_number, "msuk")
        data_dict["msuk"] = match.group(1)

        # parsing datetime
        match = cls._unsafe_search(line, line_number, "datetime")
        data_dict["datetime"] = match.group(0)

        # parsing trade direction
        match = cls._unsafe_search(line, line_number, "direction")
        data_dict["direction"] = match.group(0)

        # parsing price and trade data
        for attr in ("trade", "bid", "cbid", "ask", "cask"):
            match = cls._unsafe_search(line, line_number, attr)
            size, price = match.group(1), match.group(2)
            data_dict[attr + "Sz"] = size
            data_dict[attr + "Px"] = price

        return data_dict

    @classmethod
    def _unsafe_search(cls, line, line_number, attr):
        match_result = cls._compiled_regexes[attr].search(line)
        if match_result is None:
            raise RuntimeError(f"Failed parsing attribute `{attr}` on line number `{line_number}`.")
        return match_result
