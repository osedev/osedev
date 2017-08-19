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

from django.db.models.aggregates import Sum
from django.db.models.aggregates import Count
from django.db.models.functions import ExtractWeek, Substr
#from mediawiki_auth.models import MediaWikiUser, Revision
from random import randint

from ose.apps.user.models import User
from ose.apps.notebook.models import Entry


def global_effort(start_of_effort):
    return (
        Entry.objects
        .filter(day__gt=start_of_effort)
        .annotate(week=ExtractWeek('day'))
        .order_by('week')
        .values('week')
        .annotate(
            minutes=Sum('minutes'),
            users=Count('user', distinct=True)
        )
    )


def user_effort(start_of_effort, user):
    return (
        Entry.objects
        .filter(day__gt=start_of_effort)
        .filter(user=user)
        .annotate(week=ExtractWeek('day'))
        .order_by('week')
        .values('week')
        .annotate(minutes=Sum('minutes'))
    )


def individual_efforts(start_of_effort):

    users = User.objects.filter(
        id__in=Entry.objects
        .filter(day__gt=start_of_effort)
        .order_by('user_id')
        .values_list('user_id', flat=True)
        .distinct()
    )

    report = {
        'weeks': [r['week'] for r in global_effort(start_of_effort)],
        'users': []
    }

    if not report['weeks']:
        return report

    first_week, last_week = report['weeks'][0], report['weeks'][-1]

    for user in users:
        efforts = iter(user_effort(start_of_effort, user))
        effort = next(efforts)
        week_counter = first_week
        hours = []
        while week_counter <= last_week:
            if effort and week_counter == effort['week']:
                hours.append(effort['minutes'] / 60.0)
                try:
                    effort = next(efforts)
                except StopIteration:
                    effort = None
            else:
                hours.append(0)
            week_counter += 1
        report['users'].append({
            'color': 'rgb({}, {}, {})'.format(
                randint(1, 255),
                randint(1, 255),
                randint(1, 255),
            ),
            'hours': hours,
            'name': user.username,
        })

    return report


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
