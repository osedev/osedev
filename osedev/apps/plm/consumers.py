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

from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer
from channels.binding.websockets import WebsocketBinding
from .models import Part


class PartBinding(WebsocketBinding):
    model = Part
    stream = "plm.parts"
    fields = "name", "description"

    @classmethod
    def group_names(cls, instance):
        return cls.stream,

    def has_permission(self, user, action, pk):
        return user.is_authenticated


class PLMConsumer(JsonWebsocketConsumer):

    groups = (
        PartBinding.stream,
    )

    def connect(self, message, multiplexer=None, **kwargs):
        multiplexer.send({
            'action': 'list',
            'model': 'plm.part',
            'data': [{
                'id': part.id,
                'name': part.name,
                'description': part.description
            } for part in Part.objects.all()]
        })
