# login.py
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
from .api import _login, testCredentials, searchSchool
from .credentials import getCredentials, setCredentials

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/login.ui')
class LoginWindow(Adw.Dialog):
    __gtype_name__ = 'LoginWindow'

    login_button = Gtk.Template.Child()
    pswd_entry = Gtk.Template.Child()
    usr_entry = Gtk.Template.Child()
    school_entry = Gtk.Template.Child()
    server_entry = Gtk.Template.Child()

    search_button = Gtk.Template.Child()
    search_window = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    result_list = Gtk.Template.Child()

    sso_info_button = Gtk.Template.Child()
    sso_info_window = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window
        self.results = []

        self.login_button.connect("activated", self.login)
        self.search_button.connect("activated", self.openSearchSchoolWindow)
        self.search_entry.connect("changed", self.searchSchool)

        self.login_button.add_css_class("suggested-action")

        self.sso_info_button.connect("activated", self.openSSOInfoWindow)

    def openSSOInfoWindow(self, a = None):
        self.sso_info_window.present(self)

    def openSearchSchoolWindow(self, data = None):
        self.searchSchool()
        self.search_window.present(self)

    def searchSchool(self, data = None):
        for result in self.results:
            self.result_list.remove(result)
        self.results.clear()

        name = self.search_entry.get_text()
        schools = searchSchool(name)

        if len(schools) == 1:
            if type(schools[0]) == str:
                error = schools[0]
                if error == "too many results":
                    schools = [
                        [
                            _("Too many results"),
                            ""
                        ]
                    ]
                elif error == "offline":
                    schools = [
                        [
                            _("Offline"),
                            ""
                        ]
                    ]
                else:
                    schools = [
                        [
                            _("Error"),
                            str(error)
                        ]
                    ]
        if schools == []:
            schools = [
                [
                    _("No results"),
                    ""
                ]
            ]

        for school in schools:
            name = school[0]
            server = school[1]
            result = Adw.ButtonRow(title = name)

            def onClick(click, name=name, server=server):
                self.search_window.close()
                self.school_entry.set_text(name)
                self.server_entry.set_text(server)

            result.connect("activated", onClick)

            self.result_list.add(result)
            self.results.append(result)

    def login(self, data = None):
        print("login")
        setCredentials(user = self.usr_entry.get_text(),
                       password = self.pswd_entry.get_text(),
                       school = self.school_entry.get_text(),
                       server = self.server_entry.get_text()
                       )
        credentials = {
            "user": self.usr_entry.get_text(),
            "password": self.pswd_entry.get_text(),
            "school": self.school_entry.get_text(),
            "server": self.server_entry.get_text()
        }

        if testCredentials(credentials):
            self.close()
            self.window.shared.session.session = _login(credentials)
            self.window.timetable.loadData()

    def requestLogin(self):
        self.present(self.window)
        try:
            credentials = getCredentials()
            self.usr_entry.set_text(credentials["user"])
            self.pswd_entry.set_text(credentials["password"])
            self.school_entry.set_text(credentials["school"])
            self.server_entry.set_text(credentials["server"])
        except FileNotFoundError:
            pass # first run
