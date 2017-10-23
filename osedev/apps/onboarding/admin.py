#  Copyright (C) 2017 The OSEDev Authors.
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

from django import forms
from django.contrib import admin
from django.db.models.aggregates import Count
from .models import Application, Step
from .models import ApplicationInstance, StepValue
from .steps import widgets


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ('number', 'title', 'widget_type', 'instructions', 'widget_conf')

    def __init__(self, **kwargs):
        if 'initial' not in kwargs or not kwargs['initial']['instructions']:
            kwargs.setdefault('initial', {})
            default_widget = widgets[Step._meta.get_field('widget_type').default]
            kwargs['initial']['instructions'] = default_widget.instructions_default
            kwargs['initial']['widget_conf'] = default_widget.widget_conf_default
        super().__init__(**kwargs)
        self.fields['instructions'].help_text = self.instance.widget.instructions_help
        self.fields['widget_conf'].help_text = self.instance.widget.widget_conf_help


class StepInline(admin.StackedInline):
    model = Step
    form = StepForm
    min_num = 1
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'position', 'state', 'applications'
    )
    list_filter = (
        'state',
    )
    inlines = (
        StepInline,
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        return super().changeform_view(request, object_id, form_url, {
            'step_widgets': [{
                'name': name,
                'instructions_default': widget.instructions_default,
                'instructions_help': widget.instructions_help,
                'widget_conf_default': widget.widget_conf_default,
                'widget_conf_help': widget.widget_conf_help,
            } for name, widget in widgets.items()]
        })

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(applications_count=Count('instances'))

    def applications(self, obj):
        return obj.applications_count
    applications.short_description = 'Applications'


class StepValueInline(admin.StackedInline):
    model = StepValue


@admin.register(ApplicationInstance)
class ApplicationInstanceAdmin(admin.ModelAdmin):
    list_display = fields = readonly_fields = (
        'applicant', 'application', 'state', 'started', 'submitted', 'reviewed'
    )
    list_filter = (
        'state',
    )
    inlines = (
        StepValueInline,
    )

    def has_add_permission(self, request):
        return False
