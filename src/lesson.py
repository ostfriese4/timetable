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
    teacher_label = Gtk.Template.Child()
    room_label = Gtk.Template.Child()

    def __init__(self, lesson, window, **kwargs):
        super().__init__(**kwargs)

        click = Gtk.GestureClick.new()
        click.connect("pressed", self.on_click)
        self.add_controller(click)

        self.lesson = lesson
        self.window = window

        self.subject_label.set_label(self.lesson["subject-short"])
        self.teacher_label.set_label(self.lesson["teacher-short"])
        self.room_label.set_label(self.lesson["room"])

        self.set_size_request(-1, self.lesson["duration"])
        self.add_css_class("lesson")
        self.add_css_class(self.lesson["color"])
        if self.lesson["code"] == "cancelled":
            self.add_css_class("cancelled")
        if "original" in self.lesson:
            self.add_css_class("changed")
            if "teacher-short" in self.lesson["original"]:
                self.teacher_label.add_css_class("label")
                self.teacher_label.add_css_class("changed")
            if "subject-short" in self.lesson["original"]:
                self.subject_label.add_css_class("label")
                self.subject_label.add_css_class("changed")
            if "room" in self.lesson["original"]:
                self.room_label.add_css_class("label")
                self.room_label.add_css_class("changed")

    def on_click(self, gesture, data, x, y):
        self.window.information_window.setLesson(self.lesson)
