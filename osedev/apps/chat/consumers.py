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

from channels.generic.websockets import JsonWebsocketConsumer
from .models import Room, RoomParticipant


class ChatConsumer(JsonWebsocketConsumer):

    def connect(self, message, multiplexer=None, **kwargs):
        message.channel_session['rooms'] = []
        joined = message.user.rooms.all()
        rooms = []
        for room in joined:
            room.group.add(multiplexer.reply_channel)
            message.channel_session['rooms'].append(room.id)
            print('joining: {}'.format(room.id))
            rooms.append((room.id, room.name, room.description, True))
        for room in Room.objects.exclude(pk__in=joined).all():
            rooms.append((room.id, room.name, room.description, False))
        multiplexer.send({'rooms': rooms})

    def disconnect(self, message, multiplexer=None, **kwargs):
        for room_id in message.channel_session.get("rooms", []):
            try:
                print('leaving: {}'.format(room_id))
                room = Room.objects.get(pk=room_id)
                room.group.discard(multiplexer)
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
