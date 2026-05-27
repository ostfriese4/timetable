# homework.py
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
from gi.repository import GLib
from gi.repository import GObject
from .homework_api import getAll
from .homework_row import HomeworkRow
import datetime

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/homework.ui')
class HomeworkList(Gtk.Box):
    __gtype_name__ = 'HomeworkList'

    show_sidebar_button = Gtk.Template.Child()
    container = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayed = {}
        self.days = {}
        self.scrollTo = None

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)

        def on_visible(page, pspec):
            if parent.main_view_stack.get_visible_child_name() == "homework":
                self.displayAll()
        parent.main_view_stack.connect("notify::visible-child-name", on_visible)

        self.page = parent.homework_page
        self.displayAll()

    def scroll(self, data = None, y = None):
        if self.scrollTo is not None:
            y = self.days[self.scrollTo].get_allocation().y
        if y is not None:
            adj = self.scrolled_window.get_vadjustment()
            adj.set_value(y)

    def displayAll(self):
        unfinished = 0
        self.scrollTo = None
        data = getAll()
        for item in data:
            if item["completed"] == False:
                unfinished += 1
        self.display(data)
        self.page.set_badge_number(unfinished)
        GLib.idle_add(self.scroll)

    def sortData(self, data):
        new = []
        if not len(data) == 0:
            new.append(data.pop())
            for homework in data:
                i = 0
                date = datetime.datetime.strptime(str(homework["dueDate"]), "%Y%m%d")
                for item in new:
                    itemDate = datetime.datetime.strptime(str(item["dueDate"]), "%Y%m%d")
                    if date.year <= itemDate.year and date.month <= itemDate.month and itemDate.day <= itemDate.day:
                        break
                    i += 1
                new.insert(i,homework)
        return new

    def display(self, data):
        data = self.sortData(data)
        now = datetime.date.today()
        displayedIDs = []
        displayedDays = []
        for homework in data:
            date = homework["dueDate"]
            dt = datetime.datetime.strptime(str(date), "%Y%m%d")
            id = homework["id"]
            if not id in displayedIDs:
                displayedIDs.append(id)
            if not date in displayedDays:
                displayedDays.append(date)
            if not id in self.displayed:
                if not date in self.days:
                    dayRow = Adw.PreferencesGroup(title = dt.strftime("%d.%m.%Y"))
                    self.days[date] = dayRow
                    self.container.add(dayRow)
                dayRow = self.days[date]
                hwRow = HomeworkRow(homework)
                dayRow.add(hwRow)
                self.displayed[id] = hwRow

                if self.scrollTo is None:
                    if now.year <= dt.year:
                        if now.month <= dt.month:
                            if now.day <= dt.day:
                                self.scrollTo = date

        for id in self.displayed:
            if id not in displayedIDs:
                widget = self.displayed[id]
                parent = widget.get_parent(Adw.PreferencesGroup)
                parent.remove(widget)
                del self.displayed[id]
        for date in self.days:
            if date not in displayedDays:
                container.remove(self.days[date])
