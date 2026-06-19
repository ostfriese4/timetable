# holiday.py
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

from gi.repository import Gtk, Pango, PangoCairo, Gdk, Graphene
import math


@Gtk.Template(resource_path="/page/codeberg/ostfriese4/Untis/holiday.ui")
class Holiday(Gtk.DrawingArea):
    __gtype_name__ = "Holiday"

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.label = name
        self.set_draw_func(self.drawVerticalLabel)
        self.set_size_request(20, 20)

    def drawVerticalLabel(self, area, context, width, height):
        if Gtk.Settings.get_default().get_property("gtk-application-prefer-dark-theme"):
            context.set_source_rgb(1, 1, 1)

        layout = PangoCairo.create_layout(context)
        layout.set_text(self.label, -1)

        context.translate(width * 0.5, height * 0.5)
        context.rotate(math.pi * 0.5)
        context.translate(-height * 0.5, -width * 0.5)

        PangoCairo.update_layout(context, layout)
        PangoCairo.show_layout(context, layout)
