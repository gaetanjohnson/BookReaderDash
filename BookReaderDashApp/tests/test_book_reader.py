from unittest import TestCase
from models import BookReader, TopBookReader
from utils.data_workflow import load_data
from utils.figure_configs import FigureGenerator
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
            BookReader._validate(df)

    def test_data_workflow_cache(self):
        """
        Try to load files with cache
        """
        for file_path in DATA_TOP + DATA_LINE:
            df = load_data(file_path, use_cache=True)
            BookReader._validate(df)


class TestFigureFormatting(TestCase):

    def setUp(self) -> None:
        self.df = load_data('data_line_btc_full.data', use_cache=True)

    def test_simple_figure(self):
        features = ['bidSz', 'bidPx', 'askPx', 'askSz', 'spread']
        for feature in features:
            fig = FigureGenerator.figure(self.df, feature)
            fig.show()

    def test_bid_ask_figure(self):
        fig = FigureGenerator.bid_ask_figure(self.df)
        fig.show()

    def test_depth_cum_figure(self):
        fig = FigureGenerator.depth_cum_figure(self.df)
        fig.show()

    def test_depth_figure(self):
        fig = FigureGenerator.depth_non_cum_figure(self.df, 2)
        fig.show()

    def test_size_imbalance_figure(self):
        fig = FigureGenerator.size_imbalance_figure(self.df)
        fig.show()