from unittest import TestCase

from models import TopBookReader

from settings import DATA_DIR


class TestTopBookReader(TestCase):

    def test_load(self):
        """
        A simple exception safety and consistency check.
        """
        df = TopBookReader.load(DATA_DIR.joinpath("data_top_big.csv"))
        TopBookReader._validate(df)

        df = TopBookReader.load(DATA_DIR.joinpath("data_top.csv"))
        TopBookReader._validate(df)
