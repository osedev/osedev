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

from datetime import date, timedelta
from ose.apps.onboarding.models import Application, ApplicationInstance
from .graphs import *


def _user_applications(user):
    return user.applications.filter(
        state=ApplicationInstance.STARTED
    )


def ose(request):
    start_of_effort = date.today()-timedelta(days=7*12)
    ctx = {
        'global_effort': global_effort(start_of_effort),
        'available_applications': Application.objects.available(),
    }
    if request.user.is_authenticated:
        ctx.update({
            'user_effort': user_effort(start_of_effort, request.user),
            'user_applications': _user_applications(request.user),
        })
    return ctx
