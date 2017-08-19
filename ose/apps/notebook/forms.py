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

from django import forms
from django.utils.functional import cached_property
from .models import Entry


class DecimalMinuteHoursField(forms.DecimalField):
    """
    This form field allows editing a minute based
    model field using an hour decimal conversion.
    Providing initial value of 60 will render
    1.0 in the input box, if user enters 1.5
    the cleaned value will be 90.
    """

    class BoundField(forms.BoundField):
        @cached_property
        def initial(self):
            data = self.form.get_initial_for_field(self.field, self.name)
            return data / 60.0 if data else ''

    def get_bound_field(self, form, field_name):
        return DecimalMinuteHoursField.BoundField(form, self, field_name)

    def clean(self, value):
        decimal = super().clean(value)
        return int(decimal * 60)


class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = 'text', 'minutes'
        labels = {
            'minutes': "Hours",
        }
        field_classes = {
            'minutes': DecimalMinuteHoursField,
        }
