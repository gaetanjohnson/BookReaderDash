from unittest import TestCase

from models import BookReader

from utils import DATA_DIR


class TestBookReader(TestCase):

    def test_load(self):
        """
        A simple exception safety and consistency check.
        """
        df = BookReader.load(DATA_DIR.joinpath("data_lines.data"))
        BookReader._validate(df)
