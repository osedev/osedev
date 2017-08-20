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

import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View, TemplateView
from ose.apps.notebook.views import CreateEntry
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
        year = date.today().year
        return super().get_context_data(
            wiki_year=year,
            individual_efforts=IndividualEffortsGraph('weekly'),
            **kwargs
        )


class EmbedGraphView(TemplateView):
    template_name = 'main/graphs/embed.html'

    def get_context_data(self, **kwargs):
        period = kwargs['period']
        graph = kwargs['graph']
        if graph == 'user':
            if kwargs.get('username'):
                return super().get_context_data(graph=UserEffortGraph(
                    period, get_object_or_404(User, username=kwargs['username'])
                ))
            else:
                return super().get_context_data(graph=IndividualEffortsGraph(period))
        elif graph == 'total':
            return super().get_context_data(graph=GlobalEffortGraph(period))
        else:
            raise NotImplementedError


class ReportView(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        today = date.today()
        if kwargs['report'] == 'everybody':
            report = GlobalEffortGraph('weekly', date(today.year-1, today.month, 1))
            for day, value in zip(report.periods, report.extrapolate(report.data)):
                if value:
                    writer.writerow([day.strftime('%m/%d/%y'), value['users'], round(value['hours']/10, 3)])
        else:
            user = get_object_or_404(User, username=kwargs['report'])
            report = UserEffortGraph('weekly', user, date(today.year-1, today.month, 1))
            for day, value in zip(report.periods, report.extrapolate(report.data)):
                if value:
                    writer.writerow([day.strftime('%m/%d/%y'), round(value['hours'], 2)])
        return response
