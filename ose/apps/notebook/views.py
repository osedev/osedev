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

from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from .models import Entry
from .forms import EntryForm


class CreateEntry(CreateView):
    form_class = EntryForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['instance'] = Entry(user=self.request.user)
        return kwargs


class UpdateEntry(UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = 'notebook/update.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        if object.user != self.request.user:
            raise PermissionDenied('This is not your log entry.')
        return object
