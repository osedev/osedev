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

from datetime import date, timedelta


def mondays(start, end):
    day = start + timedelta(days=7-start.weekday())
    while day <= end:
        yield day
        day += timedelta(days=7)


def months(start, end):
    year, month = start.year, start.month
    while year <= end.year:
        while month <= 12:
            day = date(year, month, 1)
            if day > end:
                return
            yield day
            month += 1
        year, month = year+1, 1


def years(start, end):
    year = start.year
    while year <= end.year:
        yield date(year, 1, 1)
        year += 1
