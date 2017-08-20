from unittest import TestCase
from datetime import timedelta, date
from .utils import mondays, months, years


class TestDateUtils(TestCase):

    def test_mondays(self):
        end = date(1984, 1, 18)
        start = end - timedelta(days=30)
        self.assertEqual([
            date(1983, 12, 19),
            date(1983, 12, 26),
            date(1984, 1, 2),
            date(1984, 1, 9),
            date(1984, 1, 16),
        ], list(mondays(start, end)))

    def test_months(self):
        end = date(1984, 1, 18)
        start = end - timedelta(days=90)
        self.assertEqual([
            date(1983, 10, 1),
            date(1983, 11, 1),
            date(1983, 12, 1),
            date(1984, 1, 1),
        ], list(months(start, end)))

    def test_years(self):
        end = date(2017, 1, 18)
        start = end - timedelta(days=365*4)
        self.assertEqual([
            date(2013, 1, 1),
            date(2014, 1, 1),
            date(2015, 1, 1),
            date(2016, 1, 1),
            date(2017, 1, 1),
        ], list(years(start, end)))
