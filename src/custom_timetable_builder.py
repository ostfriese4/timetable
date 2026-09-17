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
from gi.repository import GLib
from gi.repository import Gio


class CustomTimetableStep(Adw.ExpanderRow):
    def __init__(self, step, parent):
        super().__init__()
        self.data = step
        self.parent = parent


        match step["type"]:
            case "fromRealTimetable":
                self.set_title(_("Take lessons from existing timetable"))

                self.src_row = Adw.ComboRow()
                self.src_row.set_title(_("Timetable"))
                self.src_row.set_enable_search(True)
                self.src_row.set_search_match_mode(Gtk.StringFilterMatchMode.SUBSTRING)
                model = Gtk.StringList()
                for timetable in self.parent.parent.shared.session.getAvailableTimetables():
                    model.append(timetable["name"])
                self.src_row.set_model(model)
                self.add_row(self.src_row)

                self.add_button = Gtk.Button()
                self.add_button.set_icon_name("list-add-symbolic")
                self.add_button.set_tooltip_text(_("Add filter"))
                self.add_suffix(self.add_button)

class CustomTimetableBuilder:
    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.steps = []

    def loadRecipe(self, recipe):
        for step in recipe:
            stepWidget = CustomTimetableStep(step, self)
            self.steps.append(stepWidget)
            self.widget.add(stepWidget)
