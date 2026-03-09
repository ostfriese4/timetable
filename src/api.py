# api.py
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

import datetime
import json
import os
import requests
import webuntis

class untisApi:
    def __init__(self):
        self.session = None
        self.colors = {}
        self.cache = True
        self.credentialsPath = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"
        try:
            self.loadColors()
        except:
            self.writeColors() # create

    def loadColors(self):
        with open(os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-colors.json") as file:
            self.colors = json.load(file)

    def writeColors(self):
        with open(os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-colors.json", "w") as file:
            json.dump(self.colors, file, indent=4)

    def getColor(self, subject):
        if subject in self.colors:
            return self.colors[subject]
        colors = [
            (1, 0, 0), # Red
            (0, 1, 0), # Green
            (0, 0, 1), # Blue
            (0.8, 0.7, 0), # Yellow / Brown
            (1, 0, 1), # Magenta
            (0, 0.5, 0.8) # Bright Blue
        ]
        color = colors[0]
        count = 0
        for key in self.colors:
            if self.colors[key] == color:
                count += 1
        for c in colors:
            n = 0
            for key in self.colors:
                if self.colors[key] == c:
                    n += 1
            if n < count:
                count = n
                color = c
        self.colors[subject] = color
        self.writeColors()
        return color

    def getTimetable(self, start, end):
        CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-days/"
        os.system("mkdir -p " + CACHEDIR)

        day_count = (end - start).days + 1

        try:
            self.cache = False
            self.login()
            table = self.session.my_timetable(start=start, end=end).to_table()
        except Exception as e:
            self.cache = True
            try:
                data = []
                for date in (start + datetime.timedelta(n) for n in range(day_count)):
                    name = date.strftime("%Y-%m-%d")
                    print("reading cache", name)
                    with open(CACHEDIR + name) as cache:
                        data.append(json.load(cache))
                return data

            except:
                return [[]]


        data = []
        days = end-start
        days = days.days + 1
        for i in range(days):
            data.append([])

        for time in table:
            time, subjects = time
            for day in subjects:
                day, info = day
                daynr = day-start
                daynr = daynr.days
                daydata = data[daynr]
                lessondata = None
                importantKeys = [
                    "sg",
                    "code",
                    "teacher-short",
                    "room"
                ]
                for lesson in info:
                    lessondata = {}
                    lessondata["sg"] = lesson.studentGroup
                    lessondata["code"] = lesson.code
                    lessondata["start"] = lesson.start.hour * 60 + lesson.start.minute
                    lessondata["end"] = lesson.end.hour * 60 + lesson.end.minute
                    lessondata["duration"] = lessondata["end"] - lessondata["start"]
                    lessondata["teacher-long"] = lesson.teachers[0].full_name
                    lessondata["teacher-short"] = lesson.teachers[0].name
                    lessondata["subject-long"] = lesson.subjects[0].long_name
                    lessondata["subject-short"] = lesson.subjects[0].name

                    try:
                        rooms = lesson.rooms
                    except Exception:
                        rooms = []
                    if rooms == []:
                        lessondata["room"] = "???"
                        lessondata["room-info"] = _("Unknown")
                    elif len(rooms) == 1:
                        lessondata["room"] = lesson.rooms[0].name
                        lessondata["room-info"] = lesson.rooms[0].long_name
                    else:
                        lessondata["room"] = ""
                        lessondata["room-info"] = ""
                        i=len(rooms)
                        for room in rooms:
                            i-=1
                            lessondata["room"] += room.name
                            lessondata["room-info"] += room.long_name
                            if i == 1:
                                lessondata["room"] += " " + _("and") + " "
                                lessondata["room-info"] += " " + _("and") + " "
                            elif i > 1:
                                lessondata["room"] += ", "
                                lessondata["room-info"] += ", "

                    lessondata["text"] = lesson.lstext
                    if lessondata["code"] != "cancelled":
                        break # Only use the first one
                equal = True
                if len(daydata) == 0:
                    equal = False
                elif daydata[-1] is None or lessondata is None:
                    equal = False
                else:
                    for key in importantKeys:
                        if daydata[-1][key] != lessondata[key]:
                            equal = False
                if equal:
                    daydata[-1]["end"] = lessondata["end"]
                    daydata[-1]["duration"] = daydata[-1]["end"] - daydata[-1]["start"]
                else:
                    if lessondata is not None:
                        daydata.append(lessondata)


        i=0
        for date in (start + datetime.timedelta(n) for n in range(day_count)):
            name = date.strftime("%Y-%m-%d")
            print("writing cache", name)
            with open(CACHEDIR + name, "w") as cache:
                json.dump(data[i], cache, indent=4)
            i+=1

        self.logout()
        return data

    def setCredentials(self, server, school, user, password):
        with open(self.credentialsPath, "w") as file:
            json.dump({
                "username": user,
                "password": password,
                "server": server,
                "school": school
            },
            file)

    def loadCredentials(self):
        with open(self.credentialsPath) as file:
            return json.load(file)

    def login(self):
        with open(self.credentialsPath) as file:
            credentials = json.load(file)
            self.session = webuntis.Session(
                username=credentials["username"],
                password=credentials["password"],
                server=credentials["server"],
                school=credentials["school"],
                useragent='WebUntis Test'
                )
            self.session.login()

    def logout(self):
        self.session.logout()

    def testLogin(self):
        if not os.path.exists(self.credentialsPath):
            return False
        try:
            self.login()
            self.logout()
            return True
        except webuntis.errors.BadCredentialsError:
            return False
        except webuntis.errors.RemoteError:
            return False
        except requests.exceptions.ConnectionError:
            return True
        except Exception:
            return True # Unknown error


api = untisApi()
