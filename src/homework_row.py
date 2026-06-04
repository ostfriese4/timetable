# homework_row.py
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
from .homework_api import getById, setValue, getChanges

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/homework_row.ui')
class HomeworkRow(Gtk.ListBoxRow):
    __gtype_name__ = 'HomeworkRow'

    box = Gtk.Template.Child()
    check_button = Gtk.Template.Child()
    edit_button = Gtk.Template.Child()
    label = Gtk.Template.Child()
    expander = Gtk.Template.Child()

    def __init__(self, homework, **kwargs):
        super().__init__(**kwargs)

        self.homework = homework
        self.check_button.connect("toggled", self.save)
        self.edit_button.connect("clicked", self.edit)
        self.expanderItems = []
        self.update()

    def update(self):
        self.homework = getById(self.homework["id"])
        self.label.set_label(self.homework["text"])
        self.check_button.set_active(self.homework["completed"])
        self.updateExpander()

    def updateExpander(self):
        for item in self.expanderItems:
            self.expander.remove(item)
        self.expanderItems.clear()

        changes = getChanges(self.homework["id"])
        if changes == {}:
            self.expander.set_visible(False)
        else:
            self.expander.set_visible(True)
        for key in changes:
            change = changes[key]
            prop = key
            old = str(change[0])
            new = str(change[1])
            row = Adw.ActionRow(title=_("You have changed %prop from %old to %new").replace("%prop", prop).replace("%old", old).replace("%new", new))
            self.expanderItems.append(row)
            self.expander.add_row(row)

    def save(self, data = None):
        state = self.check_button.get_active()
        if state != self.homework["completed"]:
            setValue(self.homework["id"], "completed", state)
            page = self.get_ancestor(Adw.ApplicationWindow).homework_page.get_child()
            if self.is_ancestor(page):
                page.displayAll()
            else:
                diff = 1
                if state == True:
                    diff  = -1
                page.set_number(page.get_number() + diff)
        self.update()

    def edit(self, data = None):
        self.get_ancestor(Adw.ApplicationWindow).homeworkEditWindow.edit(self.homework["id"], row = self)

    def delete(self):
        self.get_ancestor(Adw.PreferencesGroup).remove(self)
