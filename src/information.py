# information.py
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

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/information.ui')
class InformationWindow(Adw.Dialog):
    __gtype_name__ = 'InformationWindow'

    info_table = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.window = window
        self.info_rows = []

    def setLesson(self, lesson):
        while self.info_rows != []:
            self.info_table.remove(self.info_rows.pop())

        data = {}

        data[_("Subject")] = lesson["subject-long"] + " (" + lesson["subject-short"] + ")"
        data[_("Room")] = lesson["room"]
        data[_("Teacher")] = lesson["teacher-long"] + " (" + lesson["teacher-short"] + ")"
        if lesson["text"] != "":
            data[_("Information about this lesson")] = lesson["text"]
        if lesson["code"] == "cancelled":
            data[_("Cancelled")] = ""
        minutes_start = lesson["start"] % 60
        hours_start = int((lesson["start"] - minutes_start) / 60)
        if len(str(minutes_start)) == 1:
            minutes_start = "0" + str(minutes_start)
        minutes_end = lesson["end"] % 60
        hours_end = int((lesson["end"] - minutes_end) / 60)
        if len(str(minutes_end)) == 1:
            minutes_end = "0" + str(minutes_end)
        data[_("Duration")] = str(lesson["duration"]) + " " + _("Minutes") + " (" + str(hours_start) + ":" + str(minutes_start) + " - " + str(hours_end) + ":" + str(minutes_end) + ")"

        if "original" in lesson:
            original = lesson["original"]
            if "subject-short" in original:
                data[_("Original subject")] = original["subject-long"] + " (" + original["subject-short"] + ")"
            if "room" in original:
                data[_("Original room")] = original["room"]
            if "teacher-short" in original:
                data[_("Original teacher")] = original["teacher-long"] + " (" + original["teacher-short"] + ")"


        for key, value in data.items():
            row = Adw.ActionRow(title = key)
            row.set_subtitle(value)
            self.info_table.add(row)
            self.info_rows.append(row)

        self.present(self.window)

