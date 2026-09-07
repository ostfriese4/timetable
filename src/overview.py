# absences.py
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
from gi.repository import GObject
from .offline_banner import OfflineBanner


@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/overview.ui")
class OverviewPage(Gtk.Box):
    __gtype_name__ = "OverviewPage"

    show_sidebar_button = Gtk.Template.Child()
    offline = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayed = []

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL,
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)

        def on_visible(page, pspec):
            if parent.main_view_stack.get_visible_child_name() == "absences":
                self.display()

        parent.main_view_stack.connect("notify::visible-child-name", on_visible)
        self.shared = parent.shared
        self.page = parent.absences_page

        try:
            absences = self.shared.session.getAbsences()
            self.count(absences)
        except:
            pass

    def display(self):
        absences = self.shared.session.getAbsences()
        self.count(absences)

        while self.displayed != []:
            row = self.displayed.pop()
            self.container.remove(row)

        for absence in absences:
            row = Absence(absence)
            self.container.add(row)
            self.displayed.append(row)
