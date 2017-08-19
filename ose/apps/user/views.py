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
from django.views.generic import TemplateView, CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ose.apps.main.graphs import user_effort
from ose.apps.notebook.models import Entry
from ose.apps.notebook.views import CreateEntry
from ose.apps.notebook.forms import EntryForm

from .models import User


class ProfileView(CreateEntry):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return ctx


class WikiView(CreateView):
    form_class = EntryForm
    template_name = 'user/wiki.html'

    def get(self, request, *args, **kwargs):
        self.profile = get_object_or_404(User, username=self.kwargs['username'])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.profile = get_object_or_404(User, username=self.kwargs['username'])
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            profile=self.profile,
            entries=self.profile.entries.all()[:20],
            user_effort=user_effort(date.today()-timedelta(days=7*12), self.profile)
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = Entry(user=self.profile)
        return kwargs

    def get_success_url(self):
        return reverse('user.wiki', kwargs={'username': self.profile.username})


class SettingsView(TemplateView):
    template_name = 'user/settings.html'

