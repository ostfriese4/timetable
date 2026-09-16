# custom_timetable_builder.py
#
# Copyright 2026 Jonas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk
from gi.repository import Adw


class CustomTimetableStep(Gtk.ListBoxItem):
    pass

class CustomTimetableBuilder:
    def __init__(self, recipe, parent):
        self.widget = parent
        self.recipe = recipe
        self.steps = []

        for step in recipe:
            stepWidget = CustomTimetableStep(step, self)
            self.steps.append(step)
            self.widget.add(step)
