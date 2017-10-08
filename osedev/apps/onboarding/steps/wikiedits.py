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

from .base import StepWidget, StepWidgetValue
from .base import widget, value_widget
from django.core.exceptions import ValidationError


@widget
class WikiEdits(StepWidget):
    instructions_default = (
        "In order to complete this step you must contribute to the OSE wiki by making at least "
        "{expected} meaningful edits; currently you have {current} edits."
    )
    instructions_help = (
        "<p>Provide instructions to user on what they need to do on the OSE wiki. "
        "Every instance of <b>{expected}</b> and <b>{current}</b> will be replaced "
        "by the minimum number of edits expected and the current number of edits "
        "a person has made.</p>"
    )
    widget_conf_default = (
        "minimum-edits: 5\n"
    )
    widget_conf_help = StepWidget.widget_conf_help + (
        "<p>Configure minimum number of wiki edits (as integer):</p>"
        "<pre>{}</pre>"
    ).format(widget_conf_default)

    def clean_instructions(self):
        try:
            self.step.instructions.format(expected=99, current=1)
        except:
            raise ValidationError("Instructions must include only {expected} and/or {current} variable placeholders.")

    def clean_widget_conf(self):
        if not self.step.widget_conf:
            raise ValidationError("The 'minimum-edits:' key is required.")
        try:
            edits = int(self.step.widget_conf['minimum-edits'])
        except KeyError:
            raise ValidationError("The 'minimum-edits:' key is required.")
        except ValueError:
            raise ValidationError("The 'minimum-edits:' value must be an integer.")
        except:
            raise ValidationError("Unknown validation error.")
        else:
            if edits < 1:
                raise ValidationError("Minimum required number of edits must be greater than 0.")


@value_widget
class WikiEditsValue(StepWidgetValue):

    def __init__(self, *args):
        super().__init__(*args)
        self.minimum_edits = int(self.value.step.widget_conf['minimum-edits'])

    def prepare(self, request):
        super().prepare(request)
        edit_count = self.request.user.mediawiki_user.edit_count
        is_acceptable = edit_count >= self.minimum_edits
        if (self.value.is_acceptable != is_acceptable or
                    self.value.value != edit_count):
            self.value.is_acceptable = is_acceptable
            self.value.value = edit_count
            self.value.save()

    @property
    def view_html(self):
        edit_count = self.value.value or 0
        is_acceptable = self.value.is_acceptable
        yield '<div class="form-group{}"><p>'.format(' has-danger' if is_acceptable else '')
        yield self.value.step.instructions.format(
            expected=self.minimum_edits, current=edit_count
        )
        yield '</p></div>'

    edit_html = view_html
