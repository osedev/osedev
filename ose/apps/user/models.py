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
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    is_osedev = models.BooleanField(
        _('OSEDev status'),
        default=False,
        help_text=_('Designates whether the user has been approved as an OSE Developer at some point in time.'),
    )

    def __str__(self):
        return "{} ({})".format(self.get_full_name(), self.get_username())


class Position(models.Model):
    name = models.CharField(max_length=512)
    weeks = models.PositiveSmallIntegerField('Term Length (weeks)')
    description = models.TextField()

    def __str__(self):
        return self.name


class UserPosition(models.Model):
    user = models.ForeignKey(User, related_name="positions", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, related_name="users", on_delete=models.PROTECT)
    term = models.ForeignKey('Term', verbose_name='Current Term', null=True)

    class Meta:
        verbose_name = "User Position"
        verbose_name_plural = "User Positions"


class Term(models.Model):
    user_position = models.ForeignKey(UserPosition, related_name="terms", on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ('-start',)

    def __str__(self):
        return '{} to {} ({:.1f} weeks)'.format(self.start, self.end, (self.end-self.start).days/7)
