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
from django.utils.timezone import now, localdate
from django.utils.translation import ugettext_lazy as _


class Part(models.Model):
    name = models.CharField(max_length=512, unique=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)


class Product(Part):

    HABITAT = "habitat"
    AGRICULTURE = "agriculture"
    INDUSTRY = "industry"
    ENERGY = "energy"
    MATERIALS = "materials"
    TRANSPORT = "transport"
    DOMESTIC = "domestic"
    COMPONENT = "component"

    CATEGORY_CHOICES = (
        (HABITAT, _("Habitat")),
        (AGRICULTURE, _("Agriculture")),
        (INDUSTRY, _("Industry")),
        (ENERGY, _("Energy")),
        (MATERIALS, _("Materials")),
        (TRANSPORT, _("Transportation")),
        (DOMESTIC, _("Domestic")),
        (COMPONENT, _("Component")),
    )
    category = models.CharField(_('Category'), default=COMPONENT, max_length=128, choices=CATEGORY_CHOICES)

    spreadsheet = models.CharField(_('Google Sheet ID'), max_length=512)
    cell = models.CharField(_('Cell'), default="'Dev'!D47", max_length=512)
    progress = models.ForeignKey('Progress', null=True, related_name="+", on_delete=models.SET_NULL)

    def import_progress(self, service):
        result = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet,
            range=self.cell
        ).execute().get('values', [])

        try:
            percent = int(result[0][0][:-1])
        except:
            return

        today = localdate()
        progress, created = Progress.objects.update_or_create(
            product=self, day=today,
            defaults={
                'product': self,
                'complete': percent,
                'day': today,
                'updated': now()
            }
        )
        if self.progress_id != progress.id:
            self.progress = progress
            self.save()


class Progress(models.Model):
    product = models.ForeignKey(Product, related_name="+", on_delete=models.CASCADE)
    complete = models.IntegerField(_("Percent Complete"))
    day = models.DateField(default=localdate)
    updated = models.DateTimeField(default=now)

    class Meta:
        ordering = '-day',
        unique_together = 'product', 'day'
