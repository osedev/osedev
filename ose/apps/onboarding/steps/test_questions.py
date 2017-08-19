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

import types
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..factories import ApplicationFactory, ApplicationInstanceFactory
from ..models import Step, StepValue


class QuestionStepAdminTests(TestCase):

    @staticmethod
    def question(instructions='* one\n* two', conf='all:\n  minimum-words: 5'):
        return Step(
            number=1, widget_type='Questions', title='B', widget_conf=conf,
            application=ApplicationFactory(),
            instructions=instructions
        )

    def test_instructions_invalid(self):
        with self.assertRaisesMessage(ValidationError, 'Must have at least one question.'):
            self.question('').full_clean()
        with self.assertRaisesMessage(ValidationError, 'Questions must begin with "*" character.'):
            self.question((
                'random text not in question\n'
                '* What is question 1?\n\nExtra.\n'
                '* Question 2.\n'
            )).full_clean()

    def test_widget_conf_invalid(self):
        with self.assertRaisesMessage(ValidationError, "'ALL' is not valid, must be 'all' or a number."):
            self.question(conf='ALL: FOO').full_clean()
        with self.assertRaisesMessage(ValidationError, "'-1' is not valid, question numbers must start at 1."):
            self.question(conf='-1:\n  minimum-words: 3').full_clean()
        with self.assertRaisesMessage(ValidationError, "'99' is not valid, there are only 2 questions."):
            self.question(conf='99:\n  minimum-words: 3').full_clean()
        with self.assertRaisesMessage(ValidationError, "'2' is missing 'minimum-words:' setting."):
            self.question(conf='2:\n  foo: 3').full_clean()

    def test_instructions_valid(self):
        step = self.question((
            '* What is question 1?\n\nExtra.\n'
            '* Question 2.\n'
        ))
        step.full_clean()  # should not raise exception
        self.assertEqual(step.widget.clean_instructions(), [
            'What is question 1?<br><br>Extra.',
            'Question 2.'
        ])


class QuestionStepValueTests(TestCase):

    @staticmethod
    def question(value=None):
        instance = ApplicationInstanceFactory()
        step = Step.objects.create(
            number=1, widget_type='Questions', title='B', widget_conf='all:\n  minimum-words: 5',
            application=instance.application,
            instructions=(
                '* What is question 1?\n\nExtra.\n'
                '* Question 2.\n'
            )
        )
        step_value = StepValue.objects.create(
            step=Step.objects.get(pk=step.pk),
            application_instance=instance,
        )
        if value is not None:
            step_value.value = value
            step_value.save()
        return step_value

    def get(self):
        request = types.SimpleNamespace()
        request.method = "GET"
        return request

    def post(self, post):
        request = types.SimpleNamespace()
        request.POST = post
        request.method = "POST"
        return request

    def test_no_prepare_render(self):
        q = self.question(['Answer 1', 'Answer 2'])
        self.assertInHTML('Answer 1', str(q.widget))

    def test_initial_get_no_errors(self):
        q = self.question()
        q.widget.prepare(self.get())
        self.assertFalse(q.is_acceptable)
        self.assertFalse(any(form.error for form in q.widget.formset))

    def test_get_with_previously_saved_invalid_shows_errors(self):
        q = self.question(['', ''])
        q.widget.prepare(self.get())
        self.assertFalse(q.is_acceptable)
        self.assertEqual(
            [form.error for form in q.widget.formset],
            ['Please include at least 5 words in your answer.',
             'Please include at least 5 words in your answer.']
        )

    def test_invalid_post_shows_errors(self):
        q = self.question()
        q.widget.prepare(self.post({
            'step-1-form-TOTAL_FORMS': '2',
            'step-1-form-INITIAL_FORMS': '2',
            'step-1-form-0-answer': '',
            'step-1-form-1-answer': '',
        }))
        self.assertFalse(q.is_acceptable)
        self.assertEqual(
            [form.error for form in q.widget.formset],
            ['Please include at least 5 words in your answer.',
             'Please include at least 5 words in your answer.']
        )

    def test_previously_saved_valid_shows_error_on_invalid_post(self):
        q = self.question(['One two three four five.']*2)
        q.widget.prepare(self.post({
            'step-1-form-TOTAL_FORMS': '2',
            'step-1-form-INITIAL_FORMS': '2',
            'step-1-form-0-answer': '',
            'step-1-form-1-answer': '',
        }))
        self.assertFalse(q.is_acceptable)
        self.assertEqual(
            [form.error for form in q.widget.formset],
            ['Please include at least 5 words in your answer.',
             'Please include at least 5 words in your answer.']
        )

    def test_short_answers(self):
        q = self.question()
        q.widget.prepare(self.post({
            'step-1-form-TOTAL_FORMS': '2',
            'step-1-form-INITIAL_FORMS': '2',
            'step-1-form-0-answer': 'This answer is long enough.',
            'step-1-form-1-answer': 'Nope.',
        }))
        self.assertFalse(q.is_acceptable)
        self.assertEqual(
            [form.error for form in q.widget.formset],
            [False, 'Please include at least 5 words in your answer. Your answer only contains 1 word(s).']
        )

    def test_acceptable(self):
        q = self.question()
        q.widget.prepare(self.post({
            'step-1-form-TOTAL_FORMS': '2',
            'step-1-form-INITIAL_FORMS': '2',
            'step-1-form-0-answer': 'This answer is long enough.',
            'step-1-form-1-answer': 'And another adequate answer here.',
        }))
        self.assertTrue(q.is_acceptable)
        self.assertEqual([form.error for form in q.widget.formset], [False, False])
