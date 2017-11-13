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
from .models import Room, RoomParticipant


class RoomBinding(WebsocketBinding):
    model = Room
    stream = "chat.rooms"
    fields = "name", "description"

    @classmethod
    def group_names(cls, instance):
        return cls.stream,

    def has_permission(self, user, action, pk):
        return False


class ChatConsumer(JsonWebsocketConsumer):

    def connect(self, message, multiplexer=None, **kwargs):
        message.channel_session['rooms'] = []
        joined = message.user.rooms.prefetch_related('users').all()
        rooms = []

        def add_room(room, **extra):
            rooms.append({
                'id': room.id,
                'name': room.name,
                'description': room.description,
                'participants': [
                    {'id': user.id, 'name': user.username} for user in room.users.all()
                ],
                **extra
            })

        for room in joined:
            room.group.add(multiplexer.reply_channel)
            message.channel_session['rooms'].append(room.id)
            add_room(room, joined=True)

        for room in Room.objects.prefetch_related('users').exclude(pk__in=joined).all():
            add_room(room, joined=False)

        multiplexer.send({
            'action': 'list',
            'model': 'chat.room',
            'data': rooms
        })

        Group(RoomBinding.stream).add(multiplexer.reply_channel)

    def disconnect(self, message, multiplexer=None, **kwargs):
        Group(RoomBinding.stream).discard(multiplexer.reply_channel)
        for room_id in message.channel_session.get("rooms", []):
            try:
                print('leaving: {}'.format(room_id))
                room = Room.objects.get(pk=room_id)
                room.group.discard(multiplexer.reply_channel)
            except Room.DoesNotExist:
                pass

    def receive(self, content, multiplexer=None, **kwargs):
        print(content)
        if 'join' in content:
            room = Room.objects.get(pk=content['join'])
            print('user {} joining {} ....'.format(self.message.user, room.name))
            RoomParticipant.objects.create(room=room, user=self.message.user)
        else:
            room = Room.objects.get(pk=content['room'])
            room.send(self.message.user, content['message'])
