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

from django.conf import settings
from apiclient import discovery
from ose.celery import app
from celery.schedules import crontab
from .models import Product


@app.task.periodic_task(run_every=crontab(minute='*/2'))
def import_progress(qs=None):
    service = discovery.build('sheets', 'v4', developerKey=settings.GOOGLE_API_KEY)
    for product in qs or Product.objects.all():
        product.import_progress(service)
