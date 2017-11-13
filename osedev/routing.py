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

from channels import route
from channels.staticfiles import StaticFilesConsumer
from channels.generic.websockets import WebsocketDemultiplexer
from django.contrib.auth import get_user_model, authenticate
from osedev.apps.chat.consumers import ChatConsumer


class OSEDevWebsocket(WebsocketDemultiplexer):
    http_user_and_session = True

    consumers = {
        'chat': ChatConsumer,
    }

    def authenticate(self):
        if not self.message.user.is_authenticated:
            if 'user_id' in self.message.channel_session:
                self.message.user = get_user_model().objects.get(pk=self.message.channel_session['user_id'])
            else:
                credentials = {}
                for key, value in self.message.content['headers']:
                    if key in (b'x-username', b'x-password'):
                        credentials[key.decode()[2:]] = value.decode()
                if len(credentials) == 2:
                    self.message.user = authenticate(**credentials)
                    self.message.channel_session['user_id'] = self.message.user.pk

    def connect(self, message, **kwargs):
        self.authenticate()
        super().connect(message, **kwargs)

    def disconnect(self, message, **kwargs):
        self.authenticate()
        super().disconnect(message, **kwargs)

    def receive(self, content, **kwargs):
        self.authenticate()
        super().receive(content, **kwargs)


channel_routing = [
    route('http.request', StaticFilesConsumer()),
    OSEDevWebsocket.as_route(),
]
