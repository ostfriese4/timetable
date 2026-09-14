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

import json
import os

shared = None
def setCustomTimetablesShared(new):
    global shared
    shared = new

def listCustomTimetables():
    try:
        with open(getPath()) as file:
            return json.load(file)
    except FileNotFoundError:
        saveCustomTimetables([])
        return []

def saveCustomTimetables(data):
    with open(getPath(), "w") as file:
        json.dump(data, file, indent = 4)

def getPath():
    return os.environ.get("XDG_DATA_HOME", ".untis/data") + f"/untis-custom-timetables-{shared.profiles['default-profile']}.json"
