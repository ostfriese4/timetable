# messages.py
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

import datetime

class Message(Adw.ExpanderRow):
    __gtype_name__ = 'Message'

    def __init__(self, message, session, **kwargs):
        super().__init__(**kwargs)

        self.set_title(message["subject"])
        self.set_subtitle(message["contentPreview"])
        self.set_subtitle_lines(1)

        self.message = message
        self.loaded = False
        self.session = session

        self.connect("notify::expanded", self.load)

    def load(self, a, b):
        if not self.loaded:
            self.loaded = True
            message = self.session.getMessageById(self.message["id"])

            content = Adw.ActionRow(title = message["content"].replace("<br>", "\n"))
            self.add_row(content)

            date = Adw.ActionRow(title = _("Date"), subtitle = datetime.datetime.strptime(self.message["sentDateTime"], "%Y-%m-%dT%H:%M:%S").strftime("%c"))
            self.add_row(date)

            sender = Adw.ActionRow(title = _("Sender"), subtitle = self.message["sender"]["displayName"])
            self.add_row(sender)

@Gtk.Template(resource_path='/page/codeberg/ostfriese4/Untis/messages.ui')
class MessagesPage(Gtk.Box):
    __gtype_name__ = 'MessagesPage'

    show_sidebar_button = Gtk.Template.Child()
    container = Gtk.Template.Child()
    news_of_day = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayed = []
        self.displayedNews = []

    def enable_bindings(self, parent):
        parent.split_view.bind_property(
            "show-sidebar",
            self.show_sidebar_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
        )
        parent.sidebar_breakpoint.add_setter(self.show_sidebar_button, "visible", True)

        def on_visible(page, pspec):
            if parent.main_view_stack.get_visible_child_name() == "messages":
                self.display()
        parent.main_view_stack.connect("notify::visible-child-name", on_visible)
        self.shared = parent.shared

    def display(self):
        messages = self.shared.session.getMessages()

        while self.displayed != []:
            row = self.displayed.pop()
            self.container.remove(row)
        while self.displayedNews != []:
            row = self.displayedNews.pop()
            self.news_of_day.remove(row)

        self.container.set_visible(True)
        for message in messages:
            row = Message(message, self.shared.session)
            self.container.add(row)
            self.displayed.append(row)
        if messages == []:
            self.container.set_visible(False)

        news = self.shared.session.getNewsOfDay()
        self.news_of_day.set_visible(True)
        for item in news:
            text = item["text"]
            text = text.replace("<br>", "\n")

            row = Adw.ActionRow(title=item["subject"], subtitle=text)
            self.news_of_day.add(row)
            self.displayedNews.append(row)
        if news == []:
            self.news_of_day.set_visible(False)
