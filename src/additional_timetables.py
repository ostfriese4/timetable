# additional_timetables.py
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
from .timetable import Timetable
from .custom_timetables import listCustomTimetables, getCustomTimetable, createCustomTimetable, setCustomTimetable
from .dialog import closeOnClickOutside
from .custom_timetable_builder import CustomTimetableBuilder

@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/additional_timetables.ui")
class AdditionalTimetablesPage(Gtk.Box):
    __gtype_name__ = "AdditionalTimetablesPage"

    show_sidebar_button = Gtk.Template.Child()
    offline = Gtk.Template.Child()
    container = Gtk.Template.Child()
    timetable_page = Gtk.Template.Child()
    view = Gtk.Template.Child()
    create_timetable_button = Gtk.Template.Child()
    edit_timetable_dialog = Gtk.Template.Child()
    recipe_name = Gtk.Template.Child()
    recipe_steps = Gtk.Template.Child()
    recipe_save = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayed = {}
        self.currentTimetable = None
        self.nested_offline = self.offline
        self.create_timetable_button.connect("clicked", self.createTimetable)
        #closeOnClickOutside(self.edit_timetable_dialog) # disabled to prevent data loss

        self.builder = CustomTimetableBuilder(self.recipe_steps, self)

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL,
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)

        def on_visible(page, pspec):
            if parent.main_view_stack.get_visible_child_name() == "additional_timetables":
                self.display()

        parent.main_view_stack.connect("notify::visible-child-name", on_visible)
        self.shared = parent.shared
        self.parent = parent

    def openTimetable(self, row, timetable):
        widget = Timetable(timetable["type"], timetable["id"])
        widget.initTimetable(self.parent)
        self.timetable_page.set_child(widget)
        self.currentTimetable = widget
        widget.offline.update(self.nested_offline.offline, self.nested_offline.last)
        self.nested_offline = widget.offline
        self.view.push(self.timetable_page)

    def refresh(self):
        if self.currentTimetable is not None:
            self.currentTimetable.refresh()
        self.display()

    def editTimetable(self, row, id):
        self.edit_timetable_dialog.present(self.parent)
        data = getCustomTimetable(id)
        self.recipe_name.set_text(data["name"])

        self.builder.loadRecipe(data["recipe"])

    def createTimetable(self, *args):
        id = createCustomTimetable()
        self.editTimetable(None, id)

    def display(self):
        timetables = listCustomTimetables()
        timetables += self.shared.session.getAvailableTimetables()

        for section in self.displayed:
            section = self.displayed[section]
            self.container.remove(section)
        self.displayed.clear()

        for timetable in timetables:
            print(timetable)
            row = Adw.ActionRow(title = timetable["name"])
            row.set_activatable(True)
            row.connect("activated", self.openTimetable, timetable)

            if timetable["type"] == "CUSTOM":
                editButton = Gtk.Button()
                editButton.set_icon_name("document-edit-symbolic")
                editButton.set_tooltip_text(_("Edit timetable"))
                editButton.connect("clicked", self.editTimetable, timetable["id"])
                row.add_suffix(editButton)

            if not timetable["type"] in self.displayed:
                title = ""
                match timetable["type"]:
                    case "STUDENT":
                        title = _("Students")
                    case "TEACHER":
                        title = _("Teachers")
                    case "CLASS":
                        title = _("Classes")
                    case "ROOM":
                        title = _("Rooms")
                    case "CUSTOM":
                        title = _("Custom timetables")

                section = Adw.PreferencesGroup(title = title)
                self.container.add(section)
                self.displayed[timetable["type"]] = section
            else:
                section = self.displayed[timetable["type"]]

            section.add(row)
