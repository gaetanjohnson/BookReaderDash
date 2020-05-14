import os

from settings import CACHE_DIR
from models import BookReader, TopBookReader
# from utils import TIME_RANGES

import re
from functools import lru_cache
from datetime import datetime as dt

APP_INPUTS = ['file_path', 'date', 'msuk', 'use_cache', 'hour', 'minute', 'second', 'micros']
TIME_RANGES = {
    'hour': {'min': 0, 'max': 24},
    'minute': {'min': 0, 'max': 60},
    'second': {'min': 0, 'max': 60},
    'microsecond': {'min': 0, 'max': 1000000}
}
def load_data(file, use_cache=False):
    """
    Load data file from supported formats.

    Parameters
    ----------
    path : pathlib.Path or str
        path or path-like object pointing to the data file.

    use_cache : bool
        if true, try to recover data from local cache.
        if false or the cache doesn't exist, invalidate the cache.

    Returns
    -------
    pandas.DataFrame
    """
    filename, file_extension = os.path.splitext(file)
    if file_extension not in ['.data', '.csv']:
        raise TypeError('File supported are .csv or .data')

    # cache now is in gitignore, this creates the directory if it doesn't exist
    CACHE_DIR.mkdir(parents=False, exist_ok=True)

    pkl_path = CACHE_DIR.joinpath(filename + ".pkl")

    if file_extension == '.data':
        reader = BookReader
    else:
        reader = TopBookReader

    if use_cache and pkl_path.exists():
        df = reader.deserialize(pkl_path)
    else:
        df = reader.load('data/' + file)
        reader.serialize(df, pkl_path)

    return df

@lru_cache(maxsize=None)
def global_store(file_path, use_cache):
    """
    Main cached function to load file from disk
    :param file_path: file to load
    :param use_cache: if using cached data to load from disk
    :return:
    """
    df = load_data(file_path, use_cache=use_cache)
    msuks = df['msuk'].unique()
    options = [{'label': msuk, 'value': msuk} for msuk in msuks]
    return df, options

def get_global_data(*args):
    """
    Intermediate function to load file from disk for clarity
    :param args: file_path abd use_cache
    :return: data from disk as a dataframe and unique msuks to display
    """
    data, msuks = global_store(*args)
    return data, msuks


@lru_cache(maxsize=None)
def filtered_data_store(**kwargs):
    """
    Main function to filter and store data from global_store
    :param kwargs: all the arguments from APP_INPUTS, given by user on the webpage
    :return: filtered data as a dataframe
    """
    file_path, date, msuk, use_cache = [kwargs.get(kwarg) for kwarg in APP_INPUTS[:4]]

    filtered_df, _ = get_global_data(file_path, use_cache)
    if msuk is not None:
        filtered_df = filtered_df[(filtered_df.msuk == msuk)]
    if date is not None:
        date = dt.strptime(re.split(r"[T ]", date)[0], '%Y-%m-%d')
        date = dt.date(date)
        filtered_df = filtered_df[(filtered_df.date == date)]
    args = [{'max': kwargs.get(f'{types}max'), 'min': kwargs.get(f'{types}min')} for types in APP_INPUTS[4:]]
    filtered_df = filter_attr(filtered_df, 'hour', args[0])
    filtered_df = filter_attr(filtered_df, 'minute', args[1])
    filtered_df = filter_attr(filtered_df, 'second', args[2])
    filtered_df = filter_attr(filtered_df, 'microsecond', args[3])

    return filtered_df


def get_filtered_data(*args):
    """
    Intermediate function for loading filtered data, in order tu convert args to kwargs
    :param args: all the inputs given by callbacks
    :return: filtered data as a dataframe
    """
    kwargs = args_to_hashable_kwargs(*args)
    data = filtered_data_store(**kwargs)
    return data


def args_to_hashable_kwargs(*args):
    """
    :param args: all the inputs given by callbacks
    :return: hashable kwargs for cached functions
    """
    ranges = [{f'{types}min': val[0], f'{types}max': val[1]} for types, val in zip(APP_INPUTS[4:], args[4:])]
    kwargs = {kwargs_name: arg for kwargs_name, arg in zip(APP_INPUTS[:4], args[:4])}
    kwargs.update({k: v for d in ranges for k, v in d.items()})
    return kwargs

def filter_attr(df, attr, timerange):
    if timerange is not None and timerange != TIME_RANGES[attr]:
        min_value, max_value = timerange['min'], timerange['max']
        return df[(df[attr] <= max_value) & (df[attr] >= min_value)]
    else:
        return df
