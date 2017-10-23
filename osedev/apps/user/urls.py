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

from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^accounts/', include('allauth.urls')),
    url(r'^settings$', login_required(SettingsView.as_view()), name="user.settings"),
    url(r'^wiki/(?P<username>[\w\. ]+)$', WikiView.as_view(), name="user.wiki"),
    url(r'^(?P<username>[\w\. ]+)$', ProfileView.as_view(), name="user.profile"),
]
