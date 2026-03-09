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
import datetime
from gi.repository import Adw
from gi.repository import Gtk

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
        self.timetable.set_draw_func(self.drawTimetable, None)
        subjectClicked = Gtk.GestureClick.new()
        subjectClicked.connect("pressed", self.subjectClicked)
        self.timetable.add_controller(subjectClicked)

        self.dim = (1,1)

        self.next_button.connect("clicked", self.next)
        self.previous_button.connect("clicked", self.previous)
        self.login_button.connect("activated", self.login)

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

    def loadData(self):
        self.table = api.getTimetable(self.startdate, self.enddate)
        if api.cache:
            if not api.testLogin():
                self.requestLogin()
            else:
                self.offline.set_revealed(revealed=True)
        else:
            self.offline.set_revealed(revealed=False)
        self.timetable.queue_draw()

    def drawTimetable(self, area, context, width, height, data):
        x=0
        start = 1440 # One day in minutes (max possible value)
        end = 0
        for day in self.table:
            for lesson in day:
                if lesson["start"] < start:
                    start = lesson["start"]
                if lesson["end"] > end:
                    end = lesson["end"]
        minutes = end-start

        self.dim = (width, height)

        for day in self.table:
            for lesson in day:
                if lesson is not None:
                    y = (height / minutes) * (lesson["start"] - start)

                    r,g,b = api.getColor(lesson["subject-short"])
                    context.set_source_rgb(r,g,b)
                    context.set_line_width(0)
                    context.rectangle(x+2, y, (width / len(self.table)) - 4, (height / minutes) * (lesson["duration"]))
                    context.fill_preserve()
                    context.stroke()


                    context.set_source_rgb(1,1,1)
                    context.move_to(x + 5,y + 10)
                    context.show_text(lesson["subject-short"])
                    context.move_to(x + 5,y + 25)
                    context.show_text(lesson["room"])
                    context.move_to(x + 5,y + 40)
                    context.show_text(lesson["teacher-short"])

                    if lesson["code"] == "cancelled":
                        context.set_source_rgb(1,1,1)
                        context.set_line_width(2)
                        context.move_to(x + 2, y)
                        context.line_to(x + (width / len(self.table)) - 2, y + (height / minutes) * (lesson["duration"]))
                        context.stroke()
                y += 20
            x += width/len(self.table)

    def subjectClicked(self, gesture, data, x, y):
        start = 1440 # One day in minutes (max possible value)
        end = 0
        for day in self.table:
            for lesson in day:
                if lesson["start"] < start:
                    start = lesson["start"]
                if lesson["end"] > end:
                    end = lesson["end"]
        minutes = end-start

        width, height = self.dim

        day = self.table[int(x / (width / len(self.table)))]
        minute = start + (y / (height / minutes))
        for subject in day:
            if subject["start"] < minute and subject["end"] > minute:
                while self.info_rows != []:
                    self.info_table.remove(self.info_rows.pop())

                data = {}

                data[_("Subject")] = subject["subject-long"] + " (" + subject["subject-short"] + ")"
                data[_("Room")] = subject["room"]
                data[_("Teacher")] = subject["teacher-long"] + " (" + subject["teacher-short"] + ")"

                for key, value in data.items():
                    row = Adw.ActionRow(title = key)
                    row.set_subtitle(value)
                    self.info_table.add(row)
                    self.info_rows.append(row)

                self.info_window.present(self)

