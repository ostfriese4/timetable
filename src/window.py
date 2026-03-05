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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timetable.set_draw_func(self.drawTimetable, None)
        self.loadData()

    def loadData(self):
        self.startdate = datetime.date(2026, 3, 2)
        self.enddate = datetime.date(2026, 3, 6)
        self.table = api.getTimetable(self.startdate, self.enddate)

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

