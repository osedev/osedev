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
from datetime import date, timedelta
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
        start_of_effort = date.today()-timedelta(days=7*12)
        return super().get_context_data(
            wiki_year=year,
            individual_efforts=individual_efforts(start_of_effort),
            **kwargs
        )


class EmbedGraphView(TemplateView):
    template_name = 'main/graphs/embed.html'

    def get_context_data(self, **kwargs):
        graph = kwargs['graph']
        start_of_effort = date.today()-timedelta(days=7*12)
        data = {}
        if graph == 'individual-efforts':
            data = {
                'individual_efforts': individual_efforts(start_of_effort),
            }
        elif graph == 'user-effort' and 'username' in kwargs:
            data = {
                'username': kwargs['username'],
                'user_effort': user_effort(
                    start_of_effort,
                    get_object_or_404(User, username=kwargs['username'])
                ),
            }
        elif graph == 'global-effort':
            pass  # added by context processor
        else:
            raise NotImplementedError
        return super().get_context_data(
            graph_html='main/graphs/{}.html'.format(graph), **data
        )


class LevelOfEffortReportView(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        for row in User.objects.annotate(minutes=Sum('entries__minutes')):
            writer.writerow([row.get_full_name(), row.minutes/60.0])
        return response
