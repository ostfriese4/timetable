# create_homework.py
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
from .homework_api import getNewId, setValue, getById

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/create_homework.ui')
class HomeworkEditWindow(Adw.Dialog):
    __gtype_name__ = 'HomeworkEditWindow'

    completed = Gtk.Template.Child()
    date = Gtk.Template.Child()
    task = Gtk.Template.Child()
    save = Gtk.Template.Child()
    subject = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.window = window
        self.save.add_css_class("suggested-action")
        self.save.connect("activated", self.on_save)

    def new_homework(self):
        self.window.main_view_stack.set_visible_child_name("homework")
        self.current_id = getNewId()
        self.task.set_text("")
        self.present(self.window)

    def on_save(self, data = None):
        setValue(self.current_id, "text", self.task.get_text())
        setValue(self.current_id, "subject", self.subject.get_text())
        setValue(self.current_id, "completed", self.completed.get_active())
        setValue(self.current_id, "dueDate", int(str(self.date.get_year()) + str(self.date.get_month()) + str(self.date.get_day())))
        self.close()
        self.window.homework.displayAll()
