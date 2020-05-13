import os

from settings import CACHE_DIR
from models import BookReader, TopBookReader


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
