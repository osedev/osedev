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

import factory
from factory import fuzzy
from osedev.apps.user.factories import UserFactory, PositionFactory

from .models import Application, ApplicationInstance, StepValue


class ApplicationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Application

    name = fuzzy.FuzzyText(length=15)
    description = fuzzy.FuzzyText(length=120)

    @classmethod
    def _create(cls, *args, **kwargs):
        if 'position' not in kwargs:
            kwargs['position'] = PositionFactory()
        return super()._create(*args, **kwargs)


class ApplicationInstanceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ApplicationInstance

    @classmethod
    def _create(cls, *args, **kwargs):
        if 'application' not in kwargs:
            kwargs['application'] = ApplicationFactory()
        if 'applicant' not in kwargs:
            kwargs['applicant'] = UserFactory()
        return super()._create(*args, **kwargs)
