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

import factory
from factory import fuzzy
from django.utils import timezone
#from django.conf import settings
#from mediawiki_auth.models import MediaWikiUser
from .models import User, Position


class PositionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Position

    name = fuzzy.FuzzyText(length=10)
    weeks = 12


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    #mediawiki_user_id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: 'user%s' % n)
    first_name = fuzzy.FuzzyText(length=5)
    last_name = fuzzy.FuzzyText(length=10)
    email = factory.LazyAttribute(lambda o: '%s@opensourceecology.org' % o.username)
    date_joined = factory.LazyFunction(timezone.now)

    @classmethod
    def _create(cls, *args, **kwargs):
        edit_count = kwargs.pop('edit_count', None)
        user = super()._create(*args, **kwargs)
        #if edit_count is not None:
        #    setattr(user, settings.MEDIAWIKI_USER_FIELD, MediaWikiUser(
        #        name=user.username, edit_count=edit_count
        #    ))
        return user