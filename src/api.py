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
import sys
import webuntis
from .credentials import getCredentials, setCredentials

class untisApi:
    def __init__(self):
        self.colors = {}
        self.cache = True
        self.CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-days/"
        os.system("mkdir -p " + self.CACHEDIR)
        try:
            self.loadColors()
        except FileNotFoundError:
            self.writeColors() # create
        try:
            self.loadCache()
        except FileNotFoundError:
            self.cacheFile = {}
            self.cacheFile["refresh"] = "01/01/2000, 00:00:00"
            self.writeCache() # create

    def getHoliday(self, date):
        path = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-holidays.json"
        load = False
        today = datetime.date.today()
        if not os.path.exists(path):
            load = True
        else:
            with open(path) as file:
                data = json.load(file)
            if today != datetime.datetime.strptime(data["updated"], "%d.%m.%y").date():
                load = True
        if load:
            try:
                self.login()
                holidays = self.session.holidays()
                self.logout()
            except Exception:
                load = False

            if load:
                data = {}
                data["updated"] = today.strftime("%d.%m.%y")
                data["holidays"] = []

                for holiday in holidays:
                    item = {}
                    item["name"] = holiday.name
                    item["start"] = holiday.start.strftime("%d.%m.%y")
                    item["end"] = holiday.end.strftime("%d.%m.%y")
                    item["short"] = holiday.short_name

                    data["holidays"].append(item)
                with open(path, "w") as file:
                    print("writing holidays-cache")
                    json.dump(data, file, indent=4)

        if not load:
            print("loading holidays-cache")
            with open(path) as file:
                data = json.load(file)
        for holiday in data["holidays"]:
            start = datetime.datetime.strptime(holiday["start"], "%d.%m.%y").date()
            end = datetime.datetime.strptime(holiday["end"], "%d.%m.%y").date()

            if start <= date and end >= date:
                return holiday

        return {
            "start": date.strftime("%d.%m.%y"),
            "end": date.strftime("%d.%m.%y"),
            "name": _("No data available")
        }

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
            "green",
            "red",
            "blue",
            "orange",
            "purple",
            "teal",
            "yellow",
            "slate",
            "pink"
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

    def loadCache(self):
        with open(self.CACHEDIR + "index.json") as cache:
            self.cacheFile = json.load(cache)

    def refresh(self):
        self.cacheFile["refresh"] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.writeCache()

    def writeCache(self):
        with open(self.CACHEDIR + "index.json", "w") as cache:
            json.dump(self.cacheFile, cache, indent = 4)

    def useCache(self, date):
        name = date.strftime("%Y-%m-%d")
        if not name in self.cacheFile:
            return False
        last = datetime.datetime.strptime(self.cacheFile[name], "%m/%d/%Y, %H:%M:%S")
        refresh = datetime.datetime.strptime(self.cacheFile["refresh"], "%m/%d/%Y, %H:%M:%S")
        now = datetime.datetime.now()
        if last <= refresh:
            return False
        if now - last >= datetime.timedelta(hours=1):
            return False
        return True

    def writeDayToCache(self, day, data):
        name = day.strftime("%Y-%m-%d")
        self.cacheFile[name] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        print("writing cache", name)
        with open(self.CACHEDIR + name, "w") as cache:
            json.dump(data, cache, indent=4)
        self.writeCache()

    def loadDayFromCache(self, day):
        name = day.strftime("%Y-%m-%d")
        print("reading cache", name)
        with open(self.CACHEDIR + name) as cache:
            return json.load(cache)

    def getTimetable(self, start, end, useCache = False):
        days = (end - start).days + 1
        self.cache = False

        useCacheOrig = useCache

        if not useCache:
            useCache = True
            for date in (start + datetime.timedelta(n) for n in range(days)):
                if not self.useCache(date):
                    useCache = False
                    break

        if not useCache:
            try:
                session = self.login()
                table = session.my_timetable(start=start, end=end).to_table()
            except webuntis.errors.DateNotAllowed:
                useCache = True
            except Exception as e:
                self.cache = True
                useCache = True
                print("offline bacause of")
                sys.print_exception(e)
        if useCache:
            try:
                data = []
                for date in (start + datetime.timedelta(n) for n in range(days)):
                    data.append(self.loadDayFromCache(date))
                return data
            except Exception:
                if days == 1:
                    return [[]]
                else:
                    data = []
                    print("Try to fetch the days individually")
                    self.cache = False
                    for date in (start + datetime.timedelta(n) for n in range(days)):
                        day = self.getTimetable(date, date, useCacheOrig)
                        data.append(day[0])
                    if data == []:
                        data.append([])
                    return data


        data = []
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
                    "room",
                    "subject-short"
                ]
                planned = None
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

                    lessondata["color"] = self.getColor(lessondata["subject-short"])

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

                    if planned is not None:
                        if lessondata["code"] == "cancelled":
                            tmp = planned
                            planned = lessondata
                            lessondata = tmp
                        original = {}
                        for key in ["room", "subject-short", "teacher-short", "subject-long", "teacher-long"]:
                            if planned[key] != lessondata[key]:
                                original[key] = planned[key]
                        lessondata["original"] = original
                    else:
                        planned = lessondata

                equal = True
                if len(daydata) == 0:
                    equal = False
                elif daydata[-1] is None or lessondata is None:
                    equal = False
                elif lessondata["start"] != daydata[-1]["end"]:
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
        for date in (start + datetime.timedelta(n) for n in range(days)):
            self.writeDayToCache(date, data[i])
            i+=1

        session.logout()
        return data

    # from https://github.com/l-koehler/untis-py (api.py)
    def school_search(self, partial_name):
        # return: [display name, server URL]

        if partial_name == "":
            return ["too many results"]

        baseurl = "https://schoolsearch.webuntis.com/schoolquery2"
        json = {
            "id": "untis-mobile-blackberry-2.7.4",
            "jsonrpc": "2.0",
            "method": "searchSchool",
            "params": [{
                "search": f"{partial_name}"
            }]
        }
        try:
            data = requests.post(url=baseurl, json=json).json()
            if "error" in data:
                return [data["error"]["message"]]
            return [
                [school["loginName"], school["server"]] for school in data["result"]["schools"]
            ]
        except requests.exceptions.ConnectionError:
            return ["offline"]

    def login(self):
        credentials = getCredentials()
        session = webuntis.Session(
            username=credentials["username"],
            password=credentials["password"],
            server=credentials["server"],
            school=credentials["school"],
            useragent='WebUntis Test'
            )
        session.login()
        return session

    def testLogin(self):
        try:
            self.login().logout()
            return True
        except webuntis.errors.BadCredentialsError:
            return False
        except webuntis.errors.RemoteError:
            return False
        except requests.exceptions.ConnectionError:
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return True # Unknown error


api = untisApi()
