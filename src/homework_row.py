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
from .homework_api import getById, setValue, delete

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/homework_row.ui')
class HomeworkRow(Gtk.ListBoxRow):
    __gtype_name__ = 'HomeworkRow'

    box = Gtk.Template.Child()
    check_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()
    label = Gtk.Template.Child()

    def __init__(self, homework, **kwargs):
        super().__init__(**kwargs)

        self.homework = homework
        self.update()
        self.check_button.connect("toggled", self.save)
        self.delete_button.add_css_class("destructive-action")
        self.delete_button.connect("clicked", self.delete)

    def update(self):
        self.homework = getById(self.homework["id"])
        self.label.set_label(self.homework["text"])
        self.check_button.set_active(self.homework["completed"])

    def save(self, data = None):
        state = self.check_button.get_active()
        if state != self.homework["completed"]:
            setValue(self.homework["id"], "completed", state)
            page = self.get_ancestor(Adw.ApplicationWindow).homework_page
            diff = 1
            if state == True:
                diff  = -1
            page.set_badge_number(page.get_badge_number() + diff)
        self.update()

    def delete(self, data=None):
        warning = Adw.AlertDialog()
        warning.set_body(_("Do you really want to delete this homework?"))
        warning.set_heading(_("Delete?"))
        warning.add_response("cancel", _("Cancel"))
        warning.add_response("delete", _("Delete"))
        warning.set_default_response("cancel")
        warning.set_close_response("cancel")
        warning.set_response_appearance("delete", 2)
        def on_answer(warning, answer):
            if answer == "delete":
                self.deleteData()
        warning.connect("response", on_answer)
        warning.present(self.get_ancestor(Adw.ApplicationWindow))

    def deleteData(self):
        delete(self.homework["id"])
        if getById(self.homework["id"]) is None:
            parent = self.get_ancestor(Adw.PreferencesGroup)
            parent.remove(self)
        else:
            self.update()

