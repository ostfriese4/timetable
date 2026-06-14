# teachers.py
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
from gi.repository import GObject

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/teachers.ui')
class TeacherPage(Gtk.Box):
    __gtype_name__ = 'TeacherPage'

    show_sidebar_button = Gtk.Template.Child()
    container = Gtk.Template.Child()
    search = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayed = []
        self.search.connect("changed", self.displayResults)

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)

        def on_visible(page, pspec):
            if parent.main_view_stack.get_visible_child_name() == "teachers":
                self.displayResults()
        parent.main_view_stack.connect("notify::visible-child-name", on_visible)
        self.shared = parent.shared

    def displayResults(self, data = None):
        term = self.search.get_text().lower()
        names = self.getAllNames()
        for name in names.copy():
            if name.lower().find(term) == -1:
                names.remove(name)
        self.display(names)

    def getAllNames(self):
        teachers = api.listTeachers()
        names = []
        for teacher in teachers:
            names.append(teacher.full_name + " (" + teacher.name + ")")
        return sorted(names)

    def display(self, teachers):
        for teacher in self.displayed:
            self.container.remove(teacher)
        self.displayed.clear()
        for teacher in teachers:
            row = Adw.ActionRow(title=teacher)
            self.container.add(row)
            self.displayed.append(row)
