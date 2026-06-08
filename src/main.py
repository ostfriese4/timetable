# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from .api import session, version, id
s = session()

from gi.repository import Gtk, Gio, Adw
from .window import UntisWindow

developers = ["Ostfriese4"]


class UntisApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='page.codeberg.ostfriese4.Untis',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/page/codeberg/ostfriese4/Untis')
        self.create_action('quit', lambda *_: self.quit(), ['<control>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('login', self.on_login_action, ['<control>l'])
        self.create_action('refresh', self.on_refresh_action, ['<control>r'])
        self.create_action('create_homework', self.on_create_homework_action, ['<control>n'])

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = UntisWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name = _('Timetable'),
                                application_icon = id,
                                developer_name   = developers[0],
                                version          = version,
                                developers       = developers,
                                copyright        = '© 2026 ' + developers[0])
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_issue_url("https://codeberg.org/ostfriese4/untis/issues")
        about.present(self.props.active_window)

    def on_login_action(self, widget, _):
        self.props.active_window.login_window.requestLogin()

    def on_refresh_action(self, widget, _):
        self.props.active_window.timetable.refresh()

    def on_create_homework_action(self, widget, _):
        self.props.active_window.homeworkEditWindow.new_homework()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = UntisApplication()

    return app.run(sys.argv)
