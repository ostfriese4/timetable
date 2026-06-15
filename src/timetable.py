# timetable.py
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
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from .homework_api import fetchHomeworks
from .information import InformationWindow
from .lesson import Lesson
from .holiday import Holiday
import datetime
import threading

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/timetable.ui')
class Timetable(Gtk.Box):
    __gtype_name__ = 'Timetable'

    overlay = Gtk.Template.Child()
    offline = Gtk.Template.Child()
    timetable = Gtk.Template.Child()
    next_button = Gtk.Template.Child()
    previous_button = Gtk.Template.Child()
    show_sidebar_button = Gtk.Template.Child()

    header_button = Gtk.Template.Child()
    date_chooser = Gtk.Template.Child()
    date_chooser_dialog = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.columns = []
        self.lessons = []
        self.overlays = []
        self.prefetching = []

        self.information_window = InformationWindow(self)

        self.next_button.connect("clicked", self.next)
        self.previous_button.connect("clicked", self.previous)
        self.header_button.connect("clicked", self.on_header_button)
        self.date_chooser.connect("day-selected", self.on_day_selected)

        self.info_rows = []

        def onSwipe(gesture,x,y):
            if abs(y) < abs(x) * 0.5:
                if x > 100:
                    self.previous()
                elif x < 100:
                    self.next()
        swipe = Gtk.GestureSwipe()
        swipe.connect("swipe", onSwipe)
        self.timetable.add_controller(swipe)

        GLib.timeout_add(1000*60, self.update_marker) # update time-marker
        GLib.timeout_add(1000*60*10, self.loadData) # Update every ten minutes (will result in every hour because of caching)

    def on_header_button(self, data=None):
        self.date_chooser.set_year(self.startdate.year)
        self.date_chooser.set_month(self.startdate.month - 1)
        self.date_chooser.set_day(self.startdate.day)
        self.date_chooser_dialog.present(self.get_ancestor(Adw.ApplicationWindow))

    def on_day_selected(self, date):
        date = datetime.datetime.strptime(self.date_chooser.get_date().format("%d-%m-%Y"), "%d-%m-%Y").date()
        self.date_chooser_dialog.close()
        self.jump_to(date)

    def jump_to(self, date):
        self.startdate = date - datetime.timedelta(days=date.weekday())
        self.enddate = self.startdate + datetime.timedelta(days=4)
        while self.enddate < date:
            self.next()
        self.loadData()

    def update_marker(self):
        for overlay in self.overlays:
            overlay[1].queue_draw()
        return True

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)
        self.shared = parent.shared

        self.jump_to(datetime.datetime.now())
        self.shared.session.getHomeworks()

    def next(self, data = None):
        self.startdate += datetime.timedelta(days=7)
        self.enddate += datetime.timedelta(days=7)
        self.loadData()

    def previous(self, data = None):
        self.startdate -= datetime.timedelta(days=7)
        self.enddate -= datetime.timedelta(days=7)
        self.loadData()

    def refresh(self):
        api.refresh()
        self.loadData()

    def prefetch(self):
        def code():
            while self.prefetching != []:
                day = self.prefetching[0]
                data = self.shared.session.getOwnTimetable(day, day)
                self.prefetching.remove(day)
            return False

        ok = (self.prefetching == [])

        start = self.startdate + datetime.timedelta(days=7)
        for date in (start + datetime.timedelta(n) for n in range(5)):
            self.prefetching.append(date)
        start = self.startdate - datetime.timedelta(days=7)
        for date in (start + datetime.timedelta(n) for n in range(5)):
            self.prefetching.append(date)

        if ok:
            thread = threading.Thread(target=code, daemon=True)
            thread.start()


    def loadData(self):
        s = self.startdate
        def load():
            try:
                table = self.shared.session.getOwnTimetable(self.startdate, self.enddate, mode = "cache")
            except:
                table = None
            if s == self.startdate:
                GLib.idle_add(self.displayData, table)
                table = self.shared.session.getOwnTimetable(self.startdate, self.enddate, mode = "normal")
                if s == self.startdate:
                    GLib.idle_add(self.displayData, table)
                    homeworks = fetchHomeworks(self.startdate, self.enddate)
                    if s == self.startdate:
                        GLib.idle_add(self.displayHomeworks, homeworks)
                        self.prefetch()
            return False

        thread = threading.Thread(target=load, daemon=True)
        thread.start()
        return True # To repeat

    def displayHomeworks(self, data):
        for homework in data:
            lessons = []
            for lesson in self.lessons:
                ld = lesson[2]
                if ld["subject"]["shortName"] == homework["subject"]:
                    if str(homework["dueDate"]) == ld["startDateTime"].strftime("%Y%m%d"):
                        lesson[1].addHomework(homework)
                        break
                if "original" in ld:
                    if "subject" in ld["original"]:
                        if ld["original"]["subject"]["shortName"] == homework["subject"]:
                            if str(homework["dueDate"]) == ld["date"]:
                                lessons.append(lesson[1])
            for lesson in lessons:
                lesson.addHomework(homework)

    def drawTimeMarker(self, area, context, width, height, dateLabel, week):
        now = datetime.datetime.now()
        y = now.hour * 60 + now.minute - self.start + dateLabel.get_allocated_height()

        #y = 200 # fake time for screenshots

        context.set_source_rgb(1, 0, 0)
        if week:
            context.set_line_width(1)
        else:
            context.set_line_width(4)
        context.move_to(0, y)
        context.line_to(width, y)
        context.stroke()

    def displayData(self, table):
        if table is None:
            return
        self.header_button.set_label(self.startdate.strftime(_("Week %W")))
        if self.shared.session.getOffline():
            self.offline.set_revealed(revealed=True)
        else:
            self.offline.set_revealed(revealed=False)

        self.start = 1440 # One day in minutes (max possible value)
        for day in table:
            for lesson in day:
                if lesson["start"] < self.start:
                    self.start = lesson["start"]

        for lesson in self.lessons:
            lesson[0].remove(lesson[1])
            lesson[1].markAsHidden()
        self.lessons.clear()

        for column in self.columns:
            self.timetable.remove(column)
        self.columns.clear()

        for overlay in self.overlays:
            overlay[0].remove_overlay(overlay[1])
        self.overlays.clear()

        date = self.startdate
        past = True
        now = datetime.datetime.now()
        for day in table:
            column = Gtk.Overlay()
            self.timetable.append(column)
            self.columns.append(column)

            dayBox = Gtk.Box()
            dayBox.set_orientation(Gtk.Orientation.VERTICAL)
            dayBox.set_hexpand(True)
            dayBox.set_halign(Gtk.Align.FILL)
            dayBox.set_spacing(0)
            column.set_child(dayBox)

            dateLabel = Gtk.Label()
            # Translators: date format in the timetable
            dateLabel.set_label(date.strftime(_("%m/%d/%y")))
            dayBox.append(dateLabel)
            dateLabel.add_css_class("day")
            if date.date() == now.date():
                dateLabel.add_css_class("today")
                timeMarker = Gtk.DrawingArea()
                timeMarker.set_hexpand(True)
                timeMarker.set_vexpand(True)
                timeMarker.set_draw_func(self.drawTimeMarker, dateLabel, False)
                timeMarker.set_can_target(False)
                column.add_overlay(timeMarker)
                self.overlays.append((column, timeMarker))

                timeMarkerWeek = Gtk.DrawingArea()
                timeMarkerWeek.set_hexpand(True)
                timeMarkerWeek.set_vexpand(True)
                timeMarkerWeek.set_draw_func(self.drawTimeMarker, dateLabel, True)
                timeMarkerWeek.set_can_target(False)
                self.overlays.append((self.overlay, timeMarkerWeek))
                self.overlay.add_overlay(timeMarkerWeek)

            x = self.start
            if day == []:
                holiday = self.shared.session.getHoliday(date)
                obj = Holiday(holiday["name"])
                dayBox.append(obj)
            for lesson in day:
                if lesson["start"] - x != 0:
                    gap = Gtk.Label()
                    gap.set_size_request(-1, lesson["start"] - x)
                    dayBox.append(gap)
                block = Lesson(lesson, self)
                x = lesson["end"]
                dayBox.append(block)
                self.lessons.append((dayBox, block, lesson))

                if past:
                    if date > now:
                        past = False
                    if date.date() == now.date():
                        if lesson["endDateTime"] >= now:
                            past = False
                if past:
                    block.add_css_class("past")

            date += datetime.timedelta(days=1)
