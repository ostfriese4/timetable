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
import webuntis

class untisApi:
    def __init__(self):
        self.session = None

    def getTimetable(self, start, end):
        CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/days/"
        os.system("mkdir -p " + CACHEDIR)

        day_count = (end - start).days + 1

        try:
            self.login()
            table = self.session.my_timetable(start=start, end=end).to_table()
            self.logout()
        except Exception as e:
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

        for time in table:
            time, subjects = time
            for day in subjects:
                day, info = day
                daynr = day-start
                daynr = daynr.days
                if len(data) == daynr:
                    data.append([])
                daydata = data[daynr]
                lessondata = None
                importantKeys = ["sg", "code", "number"]
                for lesson in info:
                    lessondata = {}
                    lessondata["sg"] = lesson.studentGroup
                    lessondata["code"] = lesson.code
                    lessondata["number"] = lesson.lsnumber
                    lessondata["start"] = lesson.start.hour * 60 + lesson.start.minute
                    lessondata["end"] = lesson.end.hour * 60 + lesson.end.minute
                    lessondata["duration"] = lessondata["end"] - lessondata["start"]
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
                    daydata.append(lessondata)


        i=0
        for date in (start + datetime.timedelta(n) for n in range(day_count)):
            name = date.strftime("%Y-%m-%d")
            print("writing cache", name)
            with open(CACHEDIR + name, "w") as cache:
                json.dump(data[i], cache, indent=4)
            i+=1

        return data

    def login(self):
        credentials = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"
        with open(credentials) as file:
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


    def test(self):
        self.login()
        for klasse in self.session.klassen():
            print(klasse.name)
        monday = datetime.date(2026, 3, 2)
        friday = datetime.date(2026, 3, 6)
        table = self.session.my_timetable(start=monday, end=friday).to_table()
        print(table)
        self.logout()

api = untisApi()
