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

from django.conf.urls import url
from .views import *
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^activity$', ActivityView.as_view(), name='activity'),
    url(r'^graphs$', GraphsView.as_view(), name='graphs'),
    url(r'^graph/(?P<period>(weekly|monthly|yearly))/(?P<graph>[\w-]+)/(?P<username>[\w ]+)?$', EmbedGraphView.as_view(), name='graph.embed'),
    url(r'^report/(?P<report>[\w ]+)\.csv$', ReportView.as_view(), name='report.csv'),
]
