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

from django.contrib import admin
from .forms import EntryForm
from .models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    fields = 'user', 'minutes', 'text', 'day'
    list_display = list_display_links = ('day', 'user', 'hours')
    list_filter = ('day',)
    date_hierarchy = 'day'

    def get_readonly_fields(self, request, obj=None):
        return ('user',) if obj else ((),)
