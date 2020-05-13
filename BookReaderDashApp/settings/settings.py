from pathlib import Path
from os import listdir


DATA_DIR = Path(__file__).parent.joinpath("../data").resolve()

CACHE_DIR = Path(__file__).parent.joinpath("../cache").resolve()

# DATA_FILES = listdir(DATA_DIR)
DATA_FILES = ['data_line_btc_full.data', 'data_line_btc.data', 'data_lines.data', 'data_lines_big.data',
              'data_top_btc_full.csv', 'data_top.csv', 'data_top_big.csv']