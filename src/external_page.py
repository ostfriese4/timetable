# external_page.py
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

import gi
gi.require_version('WebKit', '6.0')

from gi.repository import Gtk
from gi.repository import Adw
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import WebKit

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/external_page.ui')
class ExternalPage(Gtk.Box):
    __gtype_name__ = 'ExternalPage'

    show_sidebar_button = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    view = Gtk.Template.Child()
    title = Gtk.Template.Child()

    def __init__(self, data, id, **kwargs):
        super().__init__(**kwargs)
        self.loaded = False
        self.id = id
        self.data = data

        self.open_button.connect("clicked", self.open)
        self.title.set_label(data["name"])

    def open(self, data):
        Gio.AppInfo.launch_default_for_uri(self.data["redirectUrl"], None)

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)

        def on_visible(page, pspec):
            if parent.main_view_stack.get_visible_child_name() == self.id:
                if not self.loaded:
                    self.webview = WebKit.WebView()
                    self.view.append(self.webview)
                    GLib.idle_add(self.webview.load_uri, self.data["redirectUrl"])
                    self.loaded = True
        parent.main_view_stack.connect("notify::visible-child-name", on_visible)
        self.shared = parent.shared
