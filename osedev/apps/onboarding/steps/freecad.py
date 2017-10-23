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

from .base import StepWidget, widget


@widget
class FreeCADFile(StepWidget):
    instructions_default = (
        "For this position, you will be required to work with FreeCAD. To show that you know"
        "how to use FreeCAD please create and upload a FreeCAD file containing at least "
        "{expectation} 'features'."
    )
    instructions_help = (
        "Provide instructions to user on what they need to create in FreeCAD and how they will be tested."
    )
    widget_conf_default = (
        "features: 5\n"
    )
    widget_conf_help = StepWidget.widget_conf_help + (
        "<p>You may configure all questions by using the 'all' key or "
        "using question number as the key to configure individual questions:</p>"
        "<pre>{}</pre>"
    ).format(widget_conf_default)
