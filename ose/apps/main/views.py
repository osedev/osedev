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

import io
import csv
from markdown2 import markdown
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View, TemplateView
from ose.apps.notebook.views import CreateEntry
from django.db.models import Subquery, OuterRef, IntegerField
from ose.lib.utils import week_start_end
from .graphs import *


class ActivityView(TemplateView):
    template_name = 'main/activity.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            entries=Entry.objects.all()[:50], **kwargs
        )


class DashboardView(CreateEntry):
    template_name = 'main/dashboard.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            entries=Entry.objects.filter(user=self.request.user).all(), **kwargs
        )


class IndexView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            view = DashboardView.as_view()
        else:
            view = ActivityView.as_view()
        return view(request, *args, **kwargs)


class GraphsView(TemplateView):
    template_name = 'main/graphs.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            individual_efforts=IndividualEffortsGraph('weekly'),
            **kwargs
        )


class EmbedGraphView(TemplateView):
    template_name = 'main/graphs/embed.html'

    def get_context_data(self, **kwargs):
        period = kwargs['period']
        graph = kwargs['graph']
        start = self.request.GET.get('start', None)
        height = self.request.GET.get('height', None)
        try:
            m, d, y = start.split('/')
            start = datetime.date(int(y), int(m), int(d))
        except:
            start = None
        if graph == 'user':
            if kwargs.get('username'):
                return super().get_context_data(graph=UserEffortGraph(
                    get_object_or_404(User, username=kwargs['username']), period, start, height
                ))
            else:
                return super().get_context_data(graph=IndividualEffortsGraph(period, start, height))
        elif graph == 'total':
            return super().get_context_data(graph=GlobalEffortGraph(period, start, height))
        else:
            raise NotImplementedError


class CSVLogReportView(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        start = datetime.date(2017, 2, 1)
        if kwargs['report'] == 'everybody':
            report = GlobalEffortGraph('weekly', start)
            for day, value in zip(report.periods, report.extrapolate(report.data)):
                if value:
                    writer.writerow([day.strftime('%m/%d/%y'), value['users'], round(value['hours']/10, 3)])
        else:
            user = get_object_or_404(User, username=kwargs['report'])
            report = UserEffortGraph(user, 'weekly', start)
            for day, value in zip(report.periods, report.extrapolate(report.data)):
                if value:
                    writer.writerow([day.strftime('%m/%d/%y'), round(value['hours'], 2)])
        return response


class CSVEntriesView(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        entries = Entry.objects.prefetch_related('user').all()
        for entry in entries:
            writer.writerow([entry.day.strftime('%m/%d/%y'), entry.user.username, entry.hours, entry.text])
        return response


class LogReportView(TemplateView):
    template_name = 'main/log_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['logs'] = (
            Entry.objects
            .prefetch_related('user')
            .annotate(week=ExtractWeek('day'), year=ExtractISOYear('day'))
            .all()
        )
        return ctx


class Top20ReportView(TemplateView):
    template_name = 'main/top20_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if kwargs['span'] == 'week':
            day = self.request.GET.get('day', None)
            if day == 'today':
                start, end = week_start_end(now().date())
            else:
                try:
                    m, d, y = day.split('/')
                    start, end = week_start_end(datetime.date(int(y), int(m), int(d)))
                except:
                    start, end = week_start_end(now().date() - timedelta(days=7))
            ctx['title'] = 'Top 20 for {}'.format(start.strftime('%G Week %W'))
            ctx['subtitle'] = '{} - {}'.format(
                start.strftime('%b %d'),
                end.strftime('%b %d'),
            )
            qs = User.objects\
                .filter(entries__day__gte=start, entries__day__lte=end)\
                .annotate(minutes=Coalesce(Sum('entries__minutes'), 0))
        else:
            ctx['title'] = 'Top 20 of All Time'
            qs = User.objects.annotate(
                minutes=Coalesce(Sum('entries__minutes'), 0),
            )
        ctx['records'] = []
        for record in qs.order_by('-minutes')[:20]:
            ctx['records'].append({
                'hours': '{:.1f}'.format(record.minutes / 60),
                'user': record.username
            })
        return ctx


class LegalView(TemplateView):
    template_name = 'main/legal.html'

    def get_context_data(self, **kwargs):
        document = kwargs.pop('legal')
        with open('/home/lex/projects/osedev/ose/legal/{}.md'.format(document), 'r') as md:
            return super().get_context_data(
                legal=markdown(md.read(), extras=[
                    'tables', 'cuddled-lists', 'break-on-newline', 'header-ids'
                ]),
                **kwargs
            )
