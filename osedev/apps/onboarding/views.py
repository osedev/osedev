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
from django.views.generic.detail import BaseDetailView, DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Application, ApplicationInstance


class BeginApplicationProcess(BaseDetailView):
    model = Application

    def get(self, request, *args, **kwargs):
        app, created = ApplicationInstance.objects.get_or_create(
            application=self.get_object(),
            applicant=self.request.user
        )
        if created:
            app.create_values()
        return HttpResponseRedirect(reverse('application.view', kwargs={'pk': app.pk}))


class ViewApplication(DetailView):
    model = ApplicationInstance

    def get_queryset(self):
        return super().get_queryset().prefetch_related('values__steps')

    def get_object(self, queryset=None):
        object = super().get_object()
        if object.applicant != self.request.user:
            raise PermissionDenied('This is not your application form.')
        return object

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_readonly:
            return self.render_to_response(self.get_context_data())

        action = request.POST.get('action', 'save')

        if action == 'delete':
            for value in self.object.values.all():
                value.delete()
            self.object.delete()
            return HttpResponseRedirect(reverse('home'))

        self.object.prepare_values(request)

        if not self.object.started:
            self.object.start()

        if action == 'submit' and self.object.is_acceptable:
            self.object.submit()

        self.object.save()

        return self.render_to_response(self.get_context_data())
