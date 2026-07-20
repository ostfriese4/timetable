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
from .external_page import ExternalPage
from gi.repository import Adw
from gi.repository import Gtk


@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/window.ui")
class UntisWindow(Adw.ApplicationWindow):
    __gtype_name__ = "UntisWindow"

    timetable = Gtk.Template.Child()
    absences = Gtk.Template.Child()
    absences_page = Gtk.Template.Child()
    homework = Gtk.Template.Child()
    homework_page = Gtk.Template.Child()
    main_view_stack = Gtk.Template.Child()
    sidebar_breakpoint = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    teachers = Gtk.Template.Child()
    messages = Gtk.Template.Child()

    def __init__(self, shared, **kwargs):
        super().__init__(**kwargs)

        self.pages = []
        self.hiddenPages = []

        self.shared = shared
        self.login_window = LoginWindow(self)
        self.homeworkEditWindow = HomeworkEditWindow(self)
        self.profiles_window = ProfilesWindow(self)

        self.timetable.enable_bindings(self)
        self.homework.enable_bindings(self)
        self.teachers.enable_bindings(self)
        self.messages.enable_bindings(self)
        self.absences.enable_bindings(self)

        try:
            self.addExternalPages()
            self.showHideViews()
        except:
            raise

    def hidePage(self, name):
        if not name in self.hiddenPages:
            page = self.main_view_stack.get_child_by_name(name)
            self.main_view_stack.remove(page)
            self.hiddenPages.append(name)
            print("hide page",name)

    def showPage(self, name):
        if name in self.hiddenPages:
            page = self.main_view_stack.get_child_by_name(name)
            self.main_view_stack.append(page)
            self.hiddenPages.remove(name)
            print("show page",name)

    def showHideViews(self):
        if self.messages.shouldHide():
            self.hidePage("messages")
        else:
            self.showPage("messages")

    def addExternalPages(self):
        for page in self.pages:
            self.main_view_stack.remove(page)
        self.pages.clear()

        for pageData in self.shared.session.getMenu():
            id = "external" + str(len(self.pages))
            content = ExternalPage(pageData, id)

            page = self.main_view_stack.add(content)
            page.set_title(pageData["name"])
            page.set_name(id)

            content.enable_bindings(self)

            self.pages.append(page)

    def reload(self):
        self.checkCredentials()
        self.main_view_stack.set_visible_child_name("timetable")
        self.timetable.loadData()
        self.homework.displayAll()
        self.addExternalPages()
        self.showHideViews()

    def checkCredentials(self):
        print("check credentials")

        try:
            login = not testCredentials(getCredentials(self.shared.profiles["default-profile"]))
        except:
            login = True

        if login:
            self.login_window.requestLogin(self.shared.profiles["default-profile"])
        if not self.shared.session.getOffline():
            self.shared.checked = True
