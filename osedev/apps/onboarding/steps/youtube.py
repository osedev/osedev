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

from .base import StepWidget, widget


@widget
class YouTubeVideo(StepWidget):
    instructions_default = (
        "Please create and upload a {minutes} minute ({expectation} seconds} video to YouTube introducing "
        "yourself."
    )
    instructions_help = (
        "Provide instructions to user on what kind of video they need to create and how long it should be."
    )
    widget_conf_default = (
        "length: 5\n"
    )
    widget_conf_help = StepWidget.widget_conf_help + (
        "<p>Using YAML syntax, you can configure minimum video length in seconds (as integer):</p>"
        "<pre>{}</pre>"
    ).format(widget_conf_default)

    def validate(self):
        return self.value.startswith('https://www.youtube.com/watch?v=')
