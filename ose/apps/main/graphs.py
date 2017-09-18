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

import datetime
from django.template.loader import render_to_string
from django.db.models import DateTimeField
from django.db.models.aggregates import Sum
from django.db.models.aggregates import Count
from django.db.models.functions import Extract, ExtractWeek, TruncMonth, TruncYear, Coalesce
from django.utils.safestring import mark_safe
from django.utils.timezone import now, timedelta
from random import randint

from ose.apps.user.models import User
from ose.apps.notebook.models import Entry

from ose.lib.utils import mondays, months, years


@DateTimeField.register_lookup
class ExtractISOYear(Extract):
    lookup_name = 'isoyear'


class BaseGraph:
    id = None
    data = None

    PERIODS = {
        'weekly': 'Week',
        'monthly': 'Month',
        'yearly': 'Year'
    }

    def __init__(self, period, start=None, height=None):
        self.canvas = '<canvas id="{}"{}></canvas>'.format(
            self.id, ' height="{}px"'.format(height) if height else ''
        )
        self.height = height
        self.template = 'main/graphs/{}.js'.format(self.id)
        self.period = period
        self.end = now().date()
        self.start = self.get_start(start)
        self.periods = list(self.get_periods())
        self.labels = list(self.get_lables(self.periods))

    def get_start(self, start):
        if start is not None:
            return start
        elif self.period == 'weekly':
            return self.end-timedelta(days=84)
        elif self.period == 'monthly':
            start = self.end-timedelta(days=365)
            return datetime.date(start.year, start.month, 1)
        elif self.period == 'yearly':
            return datetime.date(self.end.year-3, 1, 1)
        else:
            raise LookupError

    def get_periods(self):
        generate = {
            'weekly': mondays,
            'monthly': months,
            'yearly': years
        }[self.period]
        return generate(self.start, self.end)

    def get_lables(self, periods):
        for day in periods:
            if self.period == 'weekly':
                yield mark_safe(day.strftime("%b %d"))
            elif self.period == 'monthly':
                yield mark_safe(day.strftime("%b '%y"))
            elif self.period == 'yearly':
                yield mark_safe(day.strftime("%Y"))

    def get_query(self, **kwargs):
        qs = Entry.objects.filter(day__gte=self.start, day__lte=self.end, **kwargs)
        if self.period == 'weekly':
            qs = qs.annotate(week=ExtractWeek('day'), year=ExtractISOYear('day'))
            return qs.order_by('year', 'week').values('year', 'week')
        elif self.period == 'monthly':
            qs = qs.annotate(period=TruncMonth('day'))
        elif self.period == 'yearly':
            qs = qs.annotate(period=TruncYear('day'))
        return qs.order_by('period').values('period')

    def extrapolate(self, qs):
        data = iter(qs)
        value = None

        for day in self.periods:

            value = value or next(data, None)
            if value is None:
                yield {}
                continue

            match = False
            if self.period in ('monthly', 'yearly'):
                if day.year == value['period'].year and day.month == value['period'].month:
                    match = True
            elif self.period == 'weekly':
                iso_year, iso_week_number, _ = day.isocalendar()
                if (iso_year, iso_week_number) == (value['year'], value['week']):
                    match = True
                else:
                    # somehow the value is before the 'start', fast forward values to match periods
                    while value and (iso_year, iso_week_number) > (value['year'], value['week']):
                        value = next(data, None)
                    if value and (iso_year, iso_week_number) == (value['year'], value['week']):
                        match = True

            if match:
                value['hours'] = value['minutes'] / 60.0
                yield value
                value = None
            else:
                yield {}
                # value preserved for next loop

    def get_context(self, **kwargs):
        context = {
            'graph': self,
            'element_id': self.id,
            'labels': self.labels,
            'period_type': self.period,
            'period_label': self.PERIODS[self.period]
        }
        context.update(kwargs)
        if 'data' not in context:
            context['data'] = list(self.extrapolate(self.data))
        return context

    @property
    def js(self):
        return render_to_string(self.template, self.get_context())


class UserEffortGraph(BaseGraph):
    id = 'user-effort'

    def __init__(self, user, *args):
        super().__init__(*args)
        self.user = user

    @property
    def data(self):
        return self.get_query(user=self.user).annotate(minutes=Sum('minutes'))

    def get_context(self, **kwargs):
        return super().get_context(user_name=self.user.get_full_name())


class GlobalEffortGraph(BaseGraph):
    id = 'global-effort'

    @property
    def data(self):
        return self.get_query().annotate(
            minutes=Sum('minutes'),
            users=Count('user', distinct=True)
        )


class IndividualEffortsGraph(BaseGraph):
    id = 'individual-efforts'

    @property
    def data(self):
        users = User.objects.filter(
            is_current=True,
            id__in=Entry.objects
            .filter(day__gte=self.start, day__lte=self.end)
            .order_by('user_id')
            .values_list('user_id', flat=True)
            .distinct()
        )
        for user in users:
            data = self.get_query(user=user).annotate(minutes=Sum('minutes'))
            yield {
                'color': 'rgb({}, {}, {})'.format(
                    randint(1, 255),
                    randint(1, 255),
                    randint(1, 255),
                ),
                'data': list(self.extrapolate(data)),
                'name': user.first_name+(' '+user.last_name[0]+'.' if user.last_name else ''),
            }

    def get_context(self, **kwargs):
        return super().get_context(data=list(self.data))


#def wiki_registrations():
#    return (
#        MediaWikiUser.objects
#        .annotate(year=Substr('registration', 1, 4))
#        .order_by('year')
#        .values('year')
#        .annotate(
#            users=Count('id', distinct=True)
#        )
#    )
#
#
#def wiki_revisions():
#    return (
#        Revision.objects
#        .annotate(year=Substr('rev_timestamp', 1, 4))
#        .order_by('year')
#        .values('year')
#        .annotate(
#            revisions=Count('id')
#        )
#    )
#
#
#def wiki_registrations_year(year):
#    return (
#        MediaWikiUser.objects
#        .annotate(
#            year=Substr('registration', 1, 4),
#            month=Substr('registration', 5, 2)
#        )
#        .filter(year=str(year).encode())
#        .order_by('month')
#        .values('month')
#        .annotate(
#            users=Count('id', distinct=True)
#        )
#    )
#
#
#def wiki_revisions_year(year):
#    return (
#        Revision.objects
#        .annotate(
#            year=Substr('rev_timestamp', 1, 4),
#            month=Substr('rev_timestamp', 5, 2)
#        )
#        .filter(year=str(year).encode())
#        .order_by('month')
#        .values('month')
#        .annotate(
#            revisions=Count('id')
#        )
#    )
