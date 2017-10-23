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

import types
from unittest import skip
from django.test import TestCase
from django.core.exceptions import ValidationError

from osedev.apps.user.factories import UserFactory
from ..factories import ApplicationFactory, ApplicationInstanceFactory
from ..models import Step, StepValue


@skip
class WikiEditsAdminTests(TestCase):

    @staticmethod
    def step(edits='minimum-edits: 5', instructions='WikiEdits instructions...'):
        return Step(
            number=1, widget_type='WikiEdits', title='B', widget_conf=edits,
            application=ApplicationFactory(),
            instructions=instructions
        )

    def test_instructions_invalid(self):
        with self.assertRaisesMessage(ValidationError, "Instructions must include only {expected} and/or {current} variable placeholders."):
            self.step(instructions='Foo {blah}!').full_clean()

    def test_widget_conf_invalid(self):
        with self.assertRaisesMessage(ValidationError, "The 'minimum-edits:' key is required."):
            self.step('').full_clean()
        with self.assertRaisesMessage(ValidationError, "The 'minimum-edits:' key is required."):
            self.step('other-key: 99').full_clean()
        with self.assertRaisesMessage(ValidationError, "The 'minimum-edits:' value must be an integer."):
            self.step('minimum-edits: string').full_clean()
        with self.assertRaisesMessage(ValidationError, 'Minimum required number of edits must be greater than 0.'):
            self.step('minimum-edits: 0').full_clean()
        with self.assertRaisesMessage(ValidationError, 'Minimum required number of edits must be greater than 0.'):
            self.step('minimum-edits: -1').full_clean()


@skip
class WikiEditsStepValueTests(TestCase):

    @staticmethod
    def step(value=None):
        instance = ApplicationInstanceFactory()
        step = Step.objects.create(
            number=1, widget_type='WikiEdits', title='B', widget_conf='minimum-edits: 5',
            application=instance.application,
            instructions='need: {expected}, have: {current}'
        )
        step_value = StepValue.objects.create(
            step=Step.objects.get(pk=step.pk),
            application_instance=instance,
        )
        if value is not None:
            step_value.value = value
            step_value.save()
        return step_value

    def get(self, edit_count):
        request = types.SimpleNamespace()
        request.user = UserFactory(edit_count=edit_count)
        request.method = "GET"
        return request

    def post(self, edit_count):
        request = types.SimpleNamespace()
        request.user = UserFactory(edit_count=edit_count)
        request.POST = {}
        request.method = "POST"
        return request

    def test_no_prepare_render(self):
        self.assertInHTML('need: 5, have: 99', str(self.step(99).widget))

    def test_no_errors(self):
        q = self.step()
        q.widget.prepare(self.get(6))
        self.assertTrue(q.is_acceptable)
        self.assertInHTML('need: 5, have: 6', str(q.widget))

        q.widget.prepare(self.post(7))
        self.assertTrue(q.is_acceptable)
        self.assertInHTML('need: 5, have: 7', str(q.widget))

    def test_initial_get_with_errors(self):
        q = self.step()
        q.widget.prepare(self.get(4))
        self.assertFalse(q.is_acceptable)
        self.assertInHTML('need: 5, have: 4', str(q.widget))

        q.widget.prepare(self.post(3))
        self.assertFalse(q.is_acceptable)
        self.assertInHTML('need: 5, have: 3', str(q.widget))
