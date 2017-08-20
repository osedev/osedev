from datetime import date, timedelta


def mondays(start, end):
    day = start + timedelta(days=7-start.weekday())
    while day < end:
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
