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
from .api import api

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/login.ui')
class LoginWindow(Adw.Dialog):
    __gtype_name__ = 'LoginWindow'

    login_button = Gtk.Template.Child()
    pswd_entry = Gtk.Template.Child()
    usr_entry = Gtk.Template.Child()
    school_entry = Gtk.Template.Child()
    server_entry = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window
        self.login_button.connect("activated", self.login)

    def login(self, data = None):
        print("login")
        api.setCredentials(user = self.usr_entry.get_text(),
                           password = self.pswd_entry.get_text(),
                           school = self.school_entry.get_text(),
                           server = self.server_entry.get_text()
                           )
        self.window.loadData()
        self.close()

    def requestLogin(self):
        self.present(self.window)
        try:
            credentials = api.loadCredentials()
            self.usr_entry.set_text(credentials["username"])
            self.pswd_entry.set_text(credentials["password"])
            self.school_entry.set_text(credentials["school"])
            self.server_entry.set_text(credentials["server"])
        except FileNotFoundError:
            pass # first run
