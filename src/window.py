# window.py
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

from .login import LoginWindow
from .timetable import Timetable
from .homework import HomeworkList
from .teachers import TeacherPage
from .messages import MessagesPage
from .absences import AbsencesPage
from .create_homework import HomeworkEditWindow
from .credentials import getCredentials
from .api import testCredentials
from .profiles import ProfilesWindow
from gi.repository import Adw
from gi.repository import Gtk


@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/window.ui")
class UntisWindow(Adw.ApplicationWindow):
    __gtype_name__ = "UntisWindow"

    timetable = Gtk.Template.Child()
    absences = Gtk.Template.Child()
    homework = Gtk.Template.Child()
    homework_page = Gtk.Template.Child()
    main_view_stack = Gtk.Template.Child()
    sidebar_breakpoint = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    teachers = Gtk.Template.Child()
    messages = Gtk.Template.Child()

    def __init__(self, shared, **kwargs):
        super().__init__(**kwargs)

        self.shared = shared
        self.login_window = LoginWindow(self)
        self.homeworkEditWindow = HomeworkEditWindow(self)
        self.profiles_window = ProfilesWindow(self)

        self.timetable.enable_bindings(self)
        self.homework.enable_bindings(self)
        self.teachers.enable_bindings(self)
        self.messages.enable_bindings(self)
        self.absences.enable_bindings(self)

    def reload(self):
        self.checkCredentials()
        self.main_view_stack.set_visible_child_name("timetable")
        self.timetable.loadData()
        self.homework.displayAll()

    def checkCredentials(self):
        print("check credentials")
        if not testCredentials(getCredentials(self.shared.profiles["default-profile"])):
            self.login_window.requestLogin(self.shared.profiles["default-profile"])
        if not self.shared.session.getOffline():
            self.shared.checked = True
