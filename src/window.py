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

from .api import api
from .login import LoginWindow
from .timetable import Timetable
from gi.repository import Adw
from gi.repository import Gtk


@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/window.ui')
class UntisWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UntisWindow'

    timetable = Gtk.Template.Child()
    sidebar_breakpoint = Gtk.Template.Child()
    split_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.login_window = LoginWindow(self)

        def onKeyPress(click,key,x,y):
            if key == 65363:
                self.timetable.next()
            elif key == 65361:
                self.timetable.previous()
        keyPress = Gtk.EventControllerKey.new()
        keyPress.connect("key-pressed", onKeyPress)
        self.add_controller(keyPress)
        self.timetable.enable_bindings()
