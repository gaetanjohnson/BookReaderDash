import os

from settings import CACHE_DIR
from models import BookReader, TopBookReader


def load_data(file, use_cache=False):
    """
    Explicitly ask for cache, and invalidate cache otherwise (if generator code changes)
    """
    filename, file_extension = os.path.splitext(file)

    if file_extension not in ['.data', '.csv']:
        raise TypeError('File supported are .csv or .data')

    pkl_path = CACHE_DIR.joinpath("pickle", filename + ".pkl")

    if use_cache and not pkl_path.exists(): # Maybe just create the pickle file automatically ?
        raise RuntimeError(f"File {file} is not in cache.")

    if file_extension == '.data':
        reader = BookReader
    else:
        reader = TopBookReader

    if use_cache:
        df = reader.deserialize(pkl_path)
    else:
        df = reader.load('data/' + file)
        reader.serialize(df, pkl_path)

    return df
