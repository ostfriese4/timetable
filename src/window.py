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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timetable.set_draw_func(self.drawTimetable, None)
        self.loadData()

    def loadData(self):
        api.login()
        self.startdate = datetime.date(2026, 3, 2)
        self.enddate = datetime.date(2026, 3, 6)
        self.table = api.getTimetable(self.startdate, self.enddate)
        api.logout()

    def drawTimetable(self, area, context, width, height, data):
        context.set_source_rgb(1,1,1)

        days = self.enddate - self.startdate
        days = days.days + 1 # +1 Because the current day is a day too

        for time in self.table:
            time, subjects = time
            for day in subjects:
                day, info = day
                daynr = day-self.startdate
                daynr = daynr.days
                text=""
                x=0
                y=0
                for s in info:
                    text=s.studentGroup
                    x=(width/days)*daynr
                    y=(s.start.hour - 6) * 20
                context.move_to(x, y)
                context.show_text(text)

