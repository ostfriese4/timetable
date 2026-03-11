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
from .lesson import Lesson
import datetime
from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gdk

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/window.ui')
class UntisWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UntisWindow'

    timetable = Gtk.Template.Child()
    offline = Gtk.Template.Child()
    next_button = Gtk.Template.Child()
    previous_button = Gtk.Template.Child()
    login_window = Gtk.Template.Child()
    info_window = Gtk.Template.Child()
    info_table = Gtk.Template.Child()
    login_button = Gtk.Template.Child()
    pswd_entry = Gtk.Template.Child()
    usr_entry = Gtk.Template.Child()
    school_entry = Gtk.Template.Child()
    server_entry = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.columns = []
        self.lessons = []

        self.next_button.connect("clicked", self.next)
        self.previous_button.connect("clicked", self.previous)
        self.login_button.connect("activated", self.login)

        self.connect("notify::size", self.on_size_changed)
        self.connect("realize", self.on_size_changed)

        today = datetime.date.today()
        self.startdate = today - datetime.timedelta(days=today.weekday())
        self.enddate = self.startdate + datetime.timedelta(days=4)
        self.loadData()

        self.info_rows = []

    def requestLogin(self):
        self.login_window.present(self)
        try:
            credentials = api.loadCredentials()
            self.usr_entry.set_text(credentials["username"])
            self.pswd_entry.set_text(credentials["password"])
            self.school_entry.set_text(credentials["school"])
            self.server_entry.set_text(credentials["server"])
        except FileNotFoundError:
            pass # first run

    def login(self, data = None):
        print("login")
        api.setCredentials(user = self.usr_entry.get_text(),
                           password = self.pswd_entry.get_text(),
                           school = self.school_entry.get_text(),
                           server = self.server_entry.get_text()
                           )
        self.loadData()
        self.login_window.close()

    def next(self, data = None):
        self.startdate += datetime.timedelta(days=7)
        self.enddate += datetime.timedelta(days=7)
        self.loadData()

    def previous(self, data = None):
        self.startdate -= datetime.timedelta(days=7)
        self.enddate -= datetime.timedelta(days=7)
        self.loadData()

    def on_size_changed(self, data = None):
        width = self.get_width() / len(self.columns)
        for lesson in self.lessons:
            lesson[1].setWidth(width)

    def loadData(self):
        table = api.getTimetable(self.startdate, self.enddate)
        if api.cache:
            if not api.testLogin():
                self.requestLogin()
            else:
                self.offline.set_revealed(revealed=True)
        else:
            self.offline.set_revealed(revealed=False)

        start = 1440 # One day in minutes (max possible value)
        for day in table:
            for lesson in day:
                if lesson["start"] < start:
                    start = lesson["start"]

        for lesson in self.lessons:
            lesson[0].remove(lesson[1])
        self.lessons.clear()

        for column in self.columns:
            self.timetable.remove(column)
        self.columns.clear()

        date = self.startdate
        for day in table:
            column = Gtk.Box()
            column.set_orientation(Gtk.Orientation.VERTICAL)
            column.set_hexpand(True)
            column.set_halign(Gtk.Align.FILL)
            column.set_spacing(0)
            self.timetable.append(column)
            self.columns.append(column)

            dateLabel = Gtk.Label()
            dateLabel.set_label(date.strftime("%d.%m.%y"))
            column.append(dateLabel)
            date += datetime.timedelta(days=1)

            fixed = Gtk.Fixed()
            column.append(fixed)

            for lesson in day:
                block = Lesson(lesson, self)
                fixed.put(block, 0, lesson["start"] - start)
                self.lessons.append((fixed, block))
        self.on_size_changed()
