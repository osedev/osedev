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


class ChatConsumer(JsonWebsocketConsumer):
    http_user = True
    strict_ordering = True

    def connect(self, message, multiplexer=None, **kwargs):
        multiplexer.send({'status': 'I just connected.'})

    def disconnect(self, message, **kwargs):
        pass

    def receive(self, content, multiplexer=None, **kwargs):
        multiplexer.send({'message': content})
