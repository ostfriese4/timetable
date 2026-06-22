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
from .api import session, testCredentials, searchSchool
from .credentials import getCredentials, setCredentials, setProfiles


@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/login.ui")
class LoginWindow(Adw.Dialog):
    __gtype_name__ = "LoginWindow"

    login_button = Gtk.Template.Child()
    pswd_entry = Gtk.Template.Child()
    usr_entry = Gtk.Template.Child()
    school_entry = Gtk.Template.Child()
    server_entry = Gtk.Template.Child()
    method = Gtk.Template.Child()
    profile_entry = Gtk.Template.Child()

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
        self.profile = "1"

        self.login_button.connect("activated", self.login)
        self.search_button.connect("activated", self.openSearchSchoolWindow)
        self.search_entry.connect("changed", self.searchSchool)

        self.login_button.add_css_class("suggested-action")

        self.sso_info_button.connect("activated", self.openSSOInfoWindow)
        self.method.connect("notify::selected-item", self.on_method_changed)
        self.on_method_changed()

    def openSSOInfoWindow(self, a=None):
        self.sso_info_window.present(self)

    def openSearchSchoolWindow(self, data=None):
        self.searchSchool()
        self.search_window.present(self)

    def on_method_changed(self, a=None, b=None):
        self.pswd_entry.set_title(self.method.get_selected_item().get_string())

    def searchSchool(self, data=None):
        for result in self.results:
            self.result_list.remove(result)
        self.results.clear()

        name = self.search_entry.get_text()
        schools = searchSchool(name)

        if (len(schools) and type(schools[0]) == str) or schools == []:
            if schools == []:
                error = _("No results")
            else:
                error = schools[0]
                if error == "too many results":
                    error = _("Too many results")
                elif error == "offline":
                    error = _("Offline")
                else:
                    error = _("Error")

            schools = [
                {"displayName": error, "loginName": "", "server": "", "address": ""}
            ]

        for school in schools:
            display = school["displayName"]
            name = school["loginName"]
            server = school["server"]
            address = school["address"]
            result = Adw.ActionRow(title=display, subtitle=address)
            result.set_activatable(True)
            result.set_use_markup(False)

            def onClick(click, name=name, server=server):
                if server != "":
                    self.search_window.close()
                    self.school_entry.set_text(name)
                    self.server_entry.set_text(server)

            result.connect("activated", onClick)

            self.result_list.add(result)
            self.results.append(result)

    def login(self, data=None):
        print("login")
        if self.method.get_selected_item().get_string() == _("Token"):
            credType = "token"
        else:
            credType = "password"

        setCredentials(
            user=self.usr_entry.get_text(),
            password=self.pswd_entry.get_text(),
            school=self.school_entry.get_text(),
            server=self.server_entry.get_text(),
            credType=credType,
            profile=self.profile,
        )

        self.window.shared.profiles["profiles"][self.profile]["name"] = (
            self.profile_entry.get_text()
        )
        setProfiles(self.window.shared.profiles)

        credentials = getCredentials(self.profile)
        print(credentials)
        if testCredentials(credentials):
            self.close()
            self.window.shared.session = session(credentials)
            self.window.reload()

    def fillDataFromUri(self, uri):
        print("fill", uri)
        login = "untis://setschool?"

        if uri.startswith(login):
            uri = uri[len(login):]
            data = {}
            parts = uri.split("&")
            self.method.set_selected(0)
            for part in parts:
                key, value = part.split("=")
                match key:
                    case "url":
                        self.server_entry.set_text(value)
                    case "school":
                        self.school_entry.set_text(value)
                    case "key":
                        self.pswd_entry.set_text(value)
                    case "user":
                        self.usr_entry.set_text(value)

    def requestLogin(self, profile):
        if profile is None:
            profile = "1"
        self.present(self.window)
        self.profile = profile
        print("login", profile)
        try:
            credentials = getCredentials(profile)
            self.usr_entry.set_text(credentials["user"])
            self.pswd_entry.set_text(credentials["password"])
            self.school_entry.set_text(credentials["school"])
            self.server_entry.set_text(credentials["server"])
            match credentials["type"]:
                case "token":
                    position = 0
                case "password":
                    position = 1
            self.method.set_selected(position)
        except FileNotFoundError:
            pass  # first run

        try:
            profile = self.window.shared.profiles["profiles"][self.profile]["name"]
            self.profile_entry.set_text(profile)
        except FileNotFoundError:
            pass  # first run

        profileName = self.profile_entry.get_text()
        if profileName == "":
            self.profile_entry.set_text(_("Profile") + " " + profile)
