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

import datetime
from django.db import models


class Entry(models.Model):
    text = models.TextField()
    minutes = models.IntegerField()
    user = models.ForeignKey("user.User", related_name="entries", on_delete=models.CASCADE)
    day = models.DateField(default=datetime.date.today)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"
        ordering = ('-day',)

    @property
    def hours(self):
        return self.minutes / 60
