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

from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = 'name', 'description', 'category', 'spreadsheet', 'cell'
    list_display = 'name', 'category', 'complete', 'progress_updated'

    def complete(self, obj):
        return '{}%'.format(obj.progress.complete) if obj.progress else None
    complete.short_description = _('Progress')
    complete.admin_order_field = 'progress__complete'

    def progress_updated(self, obj):
        return timesince(obj.progress.updated) + ' ago' if obj.progress else None
    progress_updated.short_description = _("Updated")
    progress_updated.admin_order_field = 'progress__updated'

    def import_progress(self, request, queryset):
        from ose.apps.plm.tasks import import_progress
        import_progress(queryset)
        self.message_user(
            request,
            "Progress updated for selected products.",
            messages.SUCCESS
        )
    import_progress.short_description = _("Import latest progress for selected products")

    actions = [import_progress]
