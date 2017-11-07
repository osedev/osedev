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
from django.db.models.aggregates import Count
from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = 'name', 'description'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomForm
    fields = 'name', 'description'
    list_display = list_display_links = 'name', 'description', 'participants', 'messages'
    search_fields = 'name', 'description'

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .annotate(participants_count=Count('participants', distinct=True))
            .annotate(messages_count=Count('messages', distinct=True))
        )

    def participants(self, obj):
        return obj.participants_count
    participants.short_description = _('Participants')
    participants.admin_order_field = 'participants_count'

    def messages(self, obj):
        return obj.messages_count
    messages.short_description = _('Messages')
    messages.admin_order_field = 'messages_count'
