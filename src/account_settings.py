# account_settings.py
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
from .dialog import closeOnClickOutside


@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/account_settings.ui")
class AccountSettingsWindow(Adw.Dialog):
    __gtype_name__ = "AccountSettingsWindow"

    email = Gtk.Template.Child()
    mail_message = Gtk.Template.Child()
    mail_notification = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.window = window
        closeOnClickOutside(self)
        self.editable = False

        self.email.connect("apply", lambda data:self.apply("email"))
        self.mail_message.connect("notify::active", lambda x,y:self.apply("forwardMessageToEmail"))
        self.mail_notification.connect("notify::active", lambda x,y:self.apply("systemMailForwarding"))

    def apply(self, key):
        if self.editable:
            match key:
                case "email":
                    value = self.email.get_text()
                case "forwardMessageToEmail":
                    value = self.mail_message.get_active()
                case "systemMailForwarding":
                    value = self.mail_notification.get_active()
            print(self.window.shared.session.setProfileKey(key, value))
            print("apply",key,value)

    def open(self, data=None):
        self.editable = False

        self.present(self.window)

        self.email.set_text(self.window.shared.session.getProfileKey("email"))
        self.mail_message.set_active(self.window.shared.session.getProfileKey("forwardMessageToEmail"))
        self.mail_notification.set_active(self.window.shared.session.getProfileKey("systemMailForwarding"))

        self.editable = True
