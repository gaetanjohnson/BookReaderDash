from unittest import TestCase
from models import BookReader, TopBookReader
from utils.data_workflow import load_data

from settings import DATA_DIR, DATA_FILES

DATA_LINE = ['data_line_btc_full.data', 'data_line_btc.data', 'data_lines.data', 'data_lines_big.data']

DATA_TOP = ['data_top_btc_full.csv', 'data_top.csv', 'data_top_big.csv']


class TestBookReader(TestCase):

    def test_load_line(self):
        """
        A simple exception safety and consistency check.
        """
        for file_path in DATA_LINE:
            df = BookReader.load(DATA_DIR.joinpath(file_path))
            BookReader._validate(df)

    def test_load_top(self):
        """
        A simple exception safety and consistency check.
        """
        for file_path in DATA_TOP:
            df = TopBookReader.load(DATA_DIR.joinpath(file_path))
            TopBookReader._validate(df)


class TestDataWorkflow(TestCase):

    def test_data_workflow(self):
        """
        Try to load files without cache
        """
        for file_path in DATA_TOP + DATA_LINE:
            df = load_data(file_path, use_cache=False)


    def test_data_workflow_cache(self):
        """
        Try to load files with cache
        """
        for file_path in DATA_TOP + DATA_LINE:
            df = load_data(file_path, use_cache=True)