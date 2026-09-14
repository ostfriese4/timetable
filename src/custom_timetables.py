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
import datetime

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

def getCustomTimetable(id):
    for timetable in listCustomTimetables():
        if timetable["id"] == id:
            return timetable
    return {
        "id": id,
        "type": "CUSTOM",
        "name": _("Unnamed"),
        "recipe": [],
    }

def setCustomTimetable(id, data):
    all = listCustomTimetables()
    for i in range (len(all)):
        if all[i][id] == id:
            all[i] = data

def createCustomTimetable():
    all = listCustomTimetables()
    id = 0
    ok = False
    while not ok:
        id += 1
        ok = True
        for item in all:
            if item["id"] == id:
                ok = False
    return id

def getKey(data, key):
    if type(key) == list:
        for i in key:
            data = data[i]
        return data
    return data[key]

def lessonMatchesFilter(lesson, filter):
    match filter["type"]:
        case "isOneOf":
            value = getKey(lesson, filter["key"])
            for item in filter["values"]:
                if item == value:
                    return True
    return False

def followStep(step, date, mode="normal"):
    data = []
    match step["type"]:
        case "fromRealTimetable":
            timetable, grid = shared.session.getTimetable(step["timetable"]["type"], step["timetable"]["id"], date, date, mode=mode)
            for lesson in timetable[0]:
                for filter in step["filters"]:
                    if (lessonMatchesFilter(lesson, filter)):
                        data.append(lesson)
                        break
    return data

def sortDay(day):
    pass

def buildCustomTimetable(id, start, end, mode = "normal"):
    recipe = getCustomTimetable(id)["recipe"]
    data = []
    dayCount = (end - start).days + 1
    for day in range(dayCount):
        dayData = []
        dayDate = start + datetime.timedelta(days = day)
        data.append(dayData)
        for step in recipe:
            dayData += followStep(step, dayDate, mode=mode)
        sortDay(dayData)
    return data, None
