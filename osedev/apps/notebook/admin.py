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

from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import truncatechars
from .forms import DecimalMinuteHoursField
from .models import Entry


class EntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = 'text', 'day', 'minutes'
        labels = {'minutes': "Hours"}
        field_classes = {'minutes': DecimalMinuteHoursField}


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    fields = 'user', 'minutes', 'text', 'day'
    list_display = list_display_links = 'day', 'user', 'hours', 'excerpt'
    list_filter = 'day',
    date_hierarchy = 'day'
    search_fields = 'user__username', 'user__first_name', 'user__last_name'

    def get_readonly_fields(self, request, obj=None):
        return ('user',) if obj else ((),)

    def hours(self, obj):
        return obj.hours
    hours.short_description = _('Hours')
    hours.admin_order_field = 'minutes'

    def excerpt(self, obj):
        return truncatechars(obj.text, 100)
    excerpt.short_description = _('Excerpt')
