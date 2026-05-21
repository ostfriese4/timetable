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
import traceback
import webuntis
from .credentials import getCredentials, setCredentials

class untisApi:
    def __init__(self):
        self.colors = {}
        self.cache = True
        self.CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-days/"
        self.holidays = []
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
        if not os.path.exists(path):
            with open(path ,"w") as file:
                self.holidays = []
                json.dump(self.holidays, file)

        useCache = self.useCacheName("holidays")

        if self.holidays == []:
            with open(path) as file:
                print("loading holidays-cache")
                self.holidays = json.load(file)
            if self.holidays == []:
                useCache = False

        if not useCache:
            try:
                session = self.login()
                holidays = session.holidays()
                session.logout()
            except Exception:
                useCache = True

            if not useCache:
                self.holidays = []
                for holiday in holidays:
                    item = {}
                    item["name"] = holiday.name
                    item["start"] = holiday.start.strftime("%d.%m.%y")
                    item["end"] = holiday.end.strftime("%d.%m.%y")
                    item["short"] = holiday.short_name

                    self.holidays.append(item)

                with open(path, "w") as file:
                    print("writing holidays-cache")
                    json.dump(self.holidays, file, indent=4)
                    self.updateCache("holidays")

        for holiday in self.holidays:
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

    def useCacheName(self, name):
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

    def useCache(self, date):
        name = date.strftime("%Y-%m-%d")
        return self.useCacheName(name)

    def updateCache(self, name):
        self.cacheFile[name] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.writeCache()

    def writeDayToCache(self, day, data):
        name = day.strftime("%Y-%m-%d")
        self.updateCache(name)
        print("writing cache", name)
        with open(self.CACHEDIR + name, "w") as cache:
            json.dump(data, cache, indent=4)

    def loadDayFromCache(self, day):
        name = day.strftime("%Y-%m-%d")
        print("reading cache", name)
        with open(self.CACHEDIR + name) as cache:
            return json.load(cache)

    def getLongName(self, item):
        if type(item) == webuntis.objects.RoomObject:
            return item.long_name
        elif type(item) == webuntis.objects.TeacherObject:
            return item.full_name
        elif type(item) == webuntis.objects.SubjectObject:
            return item.long_name
        else:
            print(type(item))
    def createList(self, items):
        if len(items) == 0:
            return "???", _("Unknown")
        long = ""
        short = ""
        i = 0
        for item in items:
            short += item.name
            long += self.getLongName(item) + " (" + item.name + ")"
            if item != items[-1]:
                short += ", "
                if i < len(items) - 2:
                    long += ", "
                else:
                    long += " " + _("and") + " "
            i += 1
        return short, long

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
                print("offline because of")
                traceback.print_exc()
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
                    lessondata["id"] = lesson.lsnumber
                    lessondata["date"] = lesson.start.strftime("%Y%m%d")
                    lessondata["start"] = lesson.start.hour * 60 + lesson.start.minute
                    lessondata["end"] = lesson.end.hour * 60 + lesson.end.minute
                    lessondata["duration"] = lessondata["end"] - lessondata["start"]

                    if len(lesson.original_teachers) != 0:
                        if not "original" in lessondata:
                            lessondata["original"] = {}
                        lessondata["original"]["teacher-short"], lessondata["original"]["teacher-long"] = self.createList(lesson.original_teachers)

                    if len(lesson.original_rooms) != 0:
                        if not "original" in lessondata:
                            lessondata["original"] = {}
                        lessondata["original"]["room"], lessondata["original"]["room-info"] = self.createList(lesson.original_rooms)


                    lessondata["subject-short"], lessondata["subject-long"] = self.createList(lesson.subjects)
                    lessondata["room"], lessondata["room-info"] = self.createList(lesson.rooms)
                    lessondata["teacher-short"], lessondata["teacher-long"] = self.createList(lesson.teachers)

                    lessondata["text"] = lesson.lstext
                    lessondata["color"] = self.getColor(lessondata["subject-short"])

                    if planned is not None:
                        if lessondata["code"] == "cancelled":
                            tmp = planned
                            planned = lessondata
                            lessondata = tmp
                        if not "original" in lessondata:
                            lessondata["original"] = {}
                        original = lessondata["original"]
                        for key in ["room", "subject-short", "teacher-short", "subject-long", "teacher-long"]:
                            if planned[key] != lessondata[key]:
                                original[key] = planned[key]
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
            "id": "page.codeberg.ostfriese4.Untis,
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
            username=credentials["user"],
            password=credentials["password"],
            server=credentials["server"],
            school=credentials["school"],
            useragent='page.codeberg.ostfriese4.Untis'
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
