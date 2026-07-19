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

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.window = window
        closeOnClickOutside(self)

    def open(self, data=None):
        self.present(self.window)
