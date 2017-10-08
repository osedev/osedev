#  Copyright (C) 2017 Lex Berezhny <lex@damoti.com>.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase
from datetime import timedelta, date
from .utils import mondays, months, years, week_start_end


class TestDateUtils(TestCase):

    def test_mondays(self):
        end = date(1984, 1, 18)
        start = end - timedelta(days=30)
        self.assertEqual([
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

    def test_week_details(self):
        self.assertEqual(
            (date(2017, 1, 16), date(2017, 1, 22)),
            week_start_end(date(2017, 1, 16))
        )
        self.assertEqual(
            (date(2017, 1, 16), date(2017, 1, 22)),
            week_start_end(date(2017, 1, 22))
        )
        self.assertEqual(
            (date(2017, 1, 16), date(2017, 1, 22)),
            week_start_end(date(2017, 1, 18))
        )
