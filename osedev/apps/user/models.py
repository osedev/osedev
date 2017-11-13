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

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
import googlemaps


class User(AbstractUser):

    email = models.EmailField('email address', unique=True)
    is_active = models.BooleanField(
        _('Valid'),
        default=True,
        help_text=_(
            'Designates this as a valid user account (eg. not spammer or fake). '
            'Un-checking this will prevent user from being able to login and '
            'is preferable to deleting accounts.'
        ),
    )
    is_osedev = models.BooleanField(
        _('OSE Developer'),
        default=False,
        help_text=_(
            'Designates whether the user has been approved as an '
            'OSE Developer at some point in time. Adds their logged '
            'time to global development effort.'
        ),
    )
    is_current = models.BooleanField(
        _('Current'),
        default=False,
        help_text=_(
            'Requires that OSE Developer status is also checked. '
            'Active OSE Developer is someone who is currently an '
            'active contributor to OSE.'
        ),
    )
    location = models.CharField(
        _('Location'),
        max_length=512,
        blank=True,
        help_text=_(
            'Used with Google Maps API to get a lat/long for mapping contributors.'
        ),
    )
    location_details = JSONField(null=True)
    latitude = models.DecimalField(_("Latitude"), null=True, max_digits=9, decimal_places=6)
    longitude = models.DecimalField(_("Longitude"), null=True, max_digits=9, decimal_places=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_location = self.location

    def __str__(self):
        return "{} ({})".format(self.get_full_name(), self.get_username())

    def clean(self):

        if self.is_current and not self.is_osedev:
            raise ValidationError({
                'is_current': _("To enable current status a user must also be an OSE Developer.")
            })

        if not self.location:
            self.latitude = None
            self.longitude = None
            self.location_details = None
        elif settings.GEOCODE_ENABLED and settings.GOOGLE_API_KEY:
            if not self.__original_location or (self.__original_location != self.location):
                gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
                self.location_details = gmaps.geocode(self.location)
                if self.location_details:
                    self.latitude = self.location_details[0]['geometry']['location']['lng']
                    self.longitude = self.location_details[0]['geometry']['location']['lat']


class Position(models.Model):
    name = models.CharField(max_length=512)
    weeks = models.PositiveSmallIntegerField('Term Length (weeks)')
    description = models.TextField()

    def __str__(self):
        return self.name


class UserPosition(models.Model):
    user = models.ForeignKey(User, related_name="positions", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, related_name="users", on_delete=models.PROTECT)
    term = models.ForeignKey('Term', verbose_name='Current Term', null=True, on_delete=models.PROTECT)

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
