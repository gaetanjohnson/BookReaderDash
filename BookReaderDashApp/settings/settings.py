from pathlib import Path
from os import listdir


DATA_DIR = Path(__file__).parent.joinpath("../data").resolve()

CACHE_DIR = Path(__file__).parent.joinpath("../cache").resolve()

DATA_FILES = listdir(DATA_DIR)