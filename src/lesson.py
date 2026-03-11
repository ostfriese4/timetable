# lesson.py
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

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/lesson.ui')
class Lesson(Gtk.Box):
    __gtype_name__ = 'Lesson'

    subject_label = Gtk.Template.Child()

    def __init__(self, lesson, window, width = -1, **kwargs):
        super().__init__(**kwargs)

        click = Gtk.GestureClick.new()
        click.connect("pressed", self.on_click)
        self.add_controller(click)

        self.lesson = lesson
        self.window = window

        self.setWidth(width)
        self.subject_label.set_label(self.lesson["subject-short"])

        self.add_css_class("lesson-card")
        self.add_css_class("lessons-" + self.lesson["color"])
        if self.lesson["code"] == "cancelled":
            self.add_css_class("lesson-cancelled")

    def setWidth(self, width):
        self.set_size_request(width, self.lesson["duration"])

    def on_click(self, gesture, data, x, y):
        while self.window.info_rows != []:
            self.window.info_table.remove(self.window.info_rows.pop())

        data = {}

        data[_("Subject")] = self.lesson["subject-long"] + " (" + self.lesson["subject-short"] + ")"
        data[_("Room")] = self.lesson["room"]
        data[_("Teacher")] = self.lesson["teacher-long"] + " (" + self.lesson["teacher-short"] + ")"
        if self.lesson["text"] != "":
            data[_("Information about this lesson")] = self.lesson["text"]
        if self.lesson["code"] == "cancelled":
            data[_("Cancelled")] = ""
        minutes_start = self.lesson["start"] % 60
        hours_start = int((self.lesson["start"] - minutes_start) / 60)
        minutes_end = self.lesson["end"] % 60
        hours_end = int((self.lesson["end"] - minutes_end) / 60)
        data[_("Duration")] = str(self.lesson["duration"]) + " " + _("Minutes") + " (" + str(hours_start) + ":" + str(minutes_start) + " - " + str(hours_end) + ":" + str(minutes_end) + ")"

        for key, value in data.items():
            row = Adw.ActionRow(title = key)
            row.set_subtitle(value)
            self.window.info_table.add(row)
            self.window.info_rows.append(row)

        self.window.info_window.present(self.window)
