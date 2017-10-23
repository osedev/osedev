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
from osedev.apps.chat.consumers import ChatConsumer
from channels.generic.websockets import WebsocketDemultiplexer


class OSEDevStreams(WebsocketDemultiplexer):
    consumers = {
        'chat': ChatConsumer
    }


channel_routing = [
    route('http.request', StaticFilesConsumer()),
    OSEDevStreams.as_route(path=r"^/streams"),
]
