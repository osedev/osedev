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

from collections import OrderedDict
from django.utils.safestring import mark_safe

widgets = OrderedDict()
value_widgets = OrderedDict()


def widget(widget_class):
    name = widget_class.__name__
    assert name not in widgets
    widgets[name] = widget_class


def value_widget(widget_class):
    name = widget_class.__name__
    assert name.endswith('Value')
    name = name[:-5]
    assert name not in value_widgets
    value_widgets[name] = widget_class


class StepWidget:

    instructions_default = ""
    instructions_help = ""
    widget_conf_default = ""
    widget_conf_help = (
        '<p>Widgets are configured using <a href="https://www.youtube.com/'
        'watch?v=W3tQPk8DNbk">YAML Syntax</a> and different options depending'
        ' on the widget.</p>'
    )

    def __init__(self, step):
        self.step = step

    def clean_instructions(self):
        pass

    def clean_widget_conf(self):
        pass


class StepWidgetValue:

    def __init__(self, value):
        self.step = value.step
        self.value = value
        self.request = None
        self.submitted = False
        self.prepared = False

    def prepare(self, request):
        self.request = request
        self.submitted = request.method == "POST"
        self.prepared = True

    @property
    def view_html(self):
        raise NotImplementedError

    @property
    def edit_html(self):
        raise NotImplementedError

    def __str__(self):
        return mark_safe('\n'.join(
            self.edit_html if self.prepared else self.view_html
        ))
