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

from django.db import models
from django.utils.timezone import now, timedelta


class Entry(models.Model):
    text = models.TextField()
    minutes = models.IntegerField()
    user = models.ForeignKey("user.User", related_name="entries", on_delete=models.CASCADE)
    day = models.DateField(default=now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"
        ordering = '-day', '-updated'

    @property
    def hours(self):
        return self.minutes / 60

    @property
    def is_editable(self):
        return self.day > now().date() - timedelta(days=8)
