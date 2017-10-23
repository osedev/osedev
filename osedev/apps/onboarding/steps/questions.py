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

from .base import StepWidget, StepWidgetValue
from .base import widget, value_widget
from django import forms
from django.core.exceptions import ValidationError


@widget
class Questions(StepWidget):
    instructions_default = (
        "* Who are you?\n"
        "* In your own words, what is Open Source Ecology?\n"
    )
    instructions_help = (
        "<p>Each question must start on a new line and begin with '<b>*</b>' character. "
        "A question may spill over across as many lines as necessary.</p>"
    )
    widget_conf_default = (
        "all:\n"
        "  minimum-words: 5\n"
    )
    widget_conf_help = StepWidget.widget_conf_help + (
        "<p>Configure all questions by using the 'all' key and for individual "
        "questions user the question number as the key.</p>"
        "<p>For example, to make all questions require 5 words but question 2 to "
        "require 10 words, it would look like this:</p>"
        "<pre>{}2:\n  minimum-words: 10\n</pre>"
    ).format(widget_conf_default)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = []

    def clean_instructions(self):
        questions = []
        question = []
        for line in self.step.instructions.splitlines():
            line = line.strip()
            if line.startswith('*'):
                if question:
                    questions.append('<br>'.join(question))
                    question = []
                line = line[1:].strip()
            elif not question:
                raise ValidationError((
                    'Questions must begin with "*" character. Line "{}"'
                    ' is not associated with any questions.').format(line)
                )
            question.append(line)
        if question:
            questions.append('<br>'.join(question))
        if not questions:
            raise ValidationError('Must have at least one question.')
        self.questions = questions
        return questions

    def clean_widget_conf(self):
        if not self.step.widget_conf:
            return
        keys = set(self.step.widget_conf.keys()) - {'all'}
        max_questions = len(self.questions)
        for key in keys:
            try:
                question = int(key)
            except ValueError:
                raise ValidationError(
                    "'{}' is not valid, must be 'all' or a number.".format(key)
                )
            else:
                if question < 1:
                    raise ValidationError(
                        "'{}' is not valid, question numbers must start at 1.".format(question)
                    )
                elif question > max_questions:
                    raise ValidationError(
                        "'{}' is not valid, there are only {} questions.".format(question, max_questions)
                    )
            try:
                self.step.widget_conf[key]['minimum-words']
            except KeyError:
                raise ValidationError(
                    "'{}' is missing 'minimum-words:' setting.".format(question)
                )


@value_widget
class QuestionsValue(StepWidgetValue):

    def __init__(self, *args):
        super().__init__(*args)
        self.formset = None
        self.questions = self.step.widget.clean_instructions()
        self.answers = self.value.value or [''] * len(self.questions)

    def prepare(self, request):
        super().prepare(request)

        prefix = 'step-{}-form'.format(self.step.number)

        data = None
        if self.submitted:
            data = self.request.POST
        elif self.value.value is not None:
            form_count = len(self.value.value)
            data = {
                prefix+'-TOTAL_FORMS': form_count,
                prefix+'-INITIAL_FORMS': form_count
            }
            for index, value in enumerate(self.value.value):
                data[prefix+'-{}-answer'.format(index)] = value

        self.formset = QuestionFormSet(
            data, prefix=prefix,
            initial=[
                {'index': i, 'question': q, 'answer': a, 'conf': self.step.widget_conf}
                for i, (q, a) in enumerate(zip(self.questions, self.answers))
            ],
        )
        self.formset.full_clean()

        if not self.submitted:
            return

        answers = []
        errors = []
        for form in self.formset:
            answers.append(form.cleaned_data['answer'])
            errors.append(form.error)

        is_acceptable = not any(errors)

        if (self.value.is_acceptable != is_acceptable or
                    self.value.value != answers):
            self.value.is_acceptable = is_acceptable
            self.value.value = answers
            self.value.save()

    @property
    def view_html(self):
        for question, answer in zip(self.questions, self.answers):
            yield '<div class="question-answer-set">'
            yield '<p class="question">{}</p>'.format(question)
            yield '<p class="answer">{}</p>'.format(answer)
            yield '</div>'

    @property
    def edit_html(self):
        yield str(self.formset.management_form)
        for form in self.formset:
            yield '<div class="form-group{}">'.format(' has-danger' if form.error else '')
            yield form['answer'].label_tag()
            if form.error:
                yield '<div class="form-control-feedback">{}</div>'.format(form.error)
            yield form['answer'].as_widget(attrs={'class': 'form-control'})
            yield '</div>'


class QuestionForm(forms.Form):
    answer = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self['answer'].label = self.initial['question']
        self.index = self.initial['index']
        self.conf = self.initial['conf']
        self.error = False

    def clean(self):
        words = len(self.cleaned_data['answer'].split())
        minimum = 0
        if self.index in self.conf:
            minimum = self.conf[self.index]['minimum-words']
        elif 'all' in self.conf:
            minimum = self.conf['all']['minimum-words']
        if minimum > words:
            self.error = (
                'Please include at least {} words in your answer.'.format(minimum) +
                (' Your answer only contains {} word(s).'.format(words) if words > 0 else '')
            )

QuestionFormSet = forms.formset_factory(QuestionForm, extra=0)
