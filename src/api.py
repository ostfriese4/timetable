import requests
import os
import json
import time
import datetime
from pathlib import Path
from hashlib import md5

version = "3.1"
id = "page.codeberg.ostfriese4.Untis"
useragent = id + " " + version

headers = {
    "User-Agent": useragent
}

offline = False

def _login(credentials):
    global offline
    s = requests.Session()
    s.headers.update(headers)
    s.headers.update({"Referer": credentials["server"] + "/"})

    try:
        form_data = {
            "school": credentials["school"],
            "j_username": credentials["user"],
            "j_password": credentials["password"],
        }

        url = credentials["server"] + "/WebUntis/j_spring_security_check"
        response = s.post(url, data=form_data)

        if response.status_code == 200:
            token = s.get(credentials["server"] + "/WebUntis/api/token/new").text
            s.headers.update({"Authorization": "Bearer " + token})
            offline = False
            return s
        else:
            print(response)
    except requests.exceptions.ConnectionError:
        offline = True
        return s # don't fail login at startup

def testCredentials(credentials):
    return _login(credentials) is not None or offline

class session:
    def __init__(self, credentials):
        self.session = _login(credentials)
        self.server = credentials["server"]

        self.name = credentials["school"] + credentials["user"]
        self.name = md5(self.name.encode()).hexdigest()
        self.CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis/" + self.name + "/"
        if not os.path.exists(self.CACHEDIR + "requests"):
            os.makedirs(self.CACHEDIR + "requests")

        self._readCacheIndex()

        try:
            with open(os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-colors.json") as file:
                self.colors = json.load(file)
        except:
            self.colors = {}

    def getOffline(self):
        return offline

    def _readCacheIndex(self):
        path = self.CACHEDIR + "index.json"
        if os.path.exists(path):
            with open(path) as file:
                self.cacheIndex = json.load(file)
        else:
            self.cacheIndex = {"last-refresh": time.time()}

    def _saveCacheIndex(self):
        path = self.CACHEDIR + "index.json"
        with open(path, "w") as file:
            json.dump(self.cacheIndex, file)

    def refresh(self):
        self.cacheIndex["last-refresh"] = time.time()
        self._saveCacheIndex()

    def _readFromCache(self, object):
        try:
            with open(self.CACHEDIR + object) as file:
                return json.load(file)
        except FileNotFoundError:
            return

    def _writeToCache(self, object, content):
        path = self.CACHEDIR + object
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        with open(path, "w") as file:
            json.dump(content, file)
            self.cacheIndex[object] = time.time()
            self._saveCacheIndex()

    def _useCache(self, object, maxage = 3600):
        if object in self.cacheIndex:
            if self.cacheIndex[object] < self.cacheIndex["last-refresh"]:
                return False
            else:
                return self.cacheIndex[object] + maxage >= time.time()
        return False

    def _getRequest(self, path, mode = "normal", maxage = 3600):
        global offline
        orig = mode
        hashed = "requests/" + md5(path.encode()).hexdigest()
        if mode == "normal":
            if self._useCache(hashed, maxage = maxage):
                mode = "cache"
            else:
                mode = "online"
        if mode == "online":
            try:
                response = self.session.get(self.server + path)
                data = response.json()
                offline = False
                if "errorCode" in data:
                    print("ERROR: PATH:", self.server + path, data)
                    mode = "cache"
                else:
                    self._writeToCache(hashed, data)
                    return data
            except requests.exceptions.ConnectionError:
                mode = "cache"
                offline = True
            except Exception:
                raise
                mode = "cache"

        if mode == "cache":
            try:
                return self._readFromCache(hashed)
            except json.decoder.JSONDecoderError:
                if orig != "online":
                    print("repairing cache", path)
                    return self.getRequest(path, "online")

    def getNewsOfDay(self, day = None):
        if day is None:
            day = datetime.date.today()
        path = "/WebUntis/api/public/news/newsWidgetData?date=" + day.strftime("%Y%m%d")
        data = self._getRequest(path)["data"]["messagesOfDay"]
        return data

    def getOwnTimetable(self, start=None, end=None, mode="normal"):
        year = self.getCurrentSchoolYear()

        s_start = datetime.datetime.strptime(year["dateRange"]["start"], "%Y-%m-%d")
        s_end = datetime.datetime.strptime(year["dateRange"]["end"], "%Y-%m-%d")
        if start is None:
            start = s_start
        if end is None or start < s_end < end:
            end = s_end

        data = []
        start = start.date()
        end = end.date()
        day = start
        while day <= end:
            path = "/WebUntis/api/rest/view/v1/timetable/entries?start=" + day.strftime("%Y-%m-%d") + "&end=" + day.strftime("%Y-%m-%d") + "&format=2&resourceType=STUDENT&resources=" + str(self.getOwnId()) + "&periodTypes=&timetableType=MY_TIMETABLE&layout=START_TIME"
            dayData = self._getRequest(path, mode)
            data.append(dayData["days"][0])
            day += datetime.timedelta(days=1)

        return self.analyzeTimetable(data, mode)

    def createList(self, data, key, long, integrate = None):
        text = ""
        i=0
        for item in data:
            text += item[key]
            if integrate is not None:
                text += " (" + item[integrate] + ")"
            if i == len(data) - 1:
                return text
            elif long and i == len(data) - 2:
                text += " " + _("and") + " "
            else:
                text += ", "
            i+=1
        if long:
            return _("Unknown")
        else:
            return "???"

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

        with open(os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-colors.json", "w") as file:
            json.dump(self.colors, file)

        return color


    def analyzeLesson(self, lesson):
        rooms = lesson["rooms"]
        old = rooms.copy()
        change = False
        for room in rooms.copy():
            if room["status"] == "REMOVED":
                change = True
                rooms.remove(room)
                room["status"] = "LATER_REMOVED"
            else:
                old.remove(room)
        if change and not "original" in lesson:
            lesson["original"] = lesson.copy()
            lesson["original"]["rooms"] = old

        start = datetime.datetime.strptime(lesson["startDateTime"], "%Y-%m-%dT%H:%M:%S")
        end = datetime.datetime.strptime(lesson["endDateTime"], "%Y-%m-%dT%H:%M:%S")
        lesson["start"] = start.hour * 60 + start.minute
        lesson["end"] = end.hour * 60 + end.minute
        lesson["duration"] = lesson["end"] - lesson["start"]
        lesson["startDateTime"] = start
        lesson["endDateTime"] = end

        if lesson["subject"] == None:
            lesson["subject"] = {
                "shortName": "???",
                "longName": _("Unknown")
            }

        lesson["teachers-short"] = self.createList(lesson["teachers"], "shortName", False)
        lesson["room"] = self.createList(rooms, "shortName", False)

        lesson["teachers-long"] = self.createList(lesson["teachers"], "longName", True, integrate = "shortName")
        lesson["room-info"] = self.createList(rooms, "longName", True)

        lesson["color"] = self.getColor(lesson["subject"]["shortName"])

        if "original" in lesson:
            lesson["original"] = self.analyzeLesson(lesson["original"])

        return lesson

    def analyzeTimetable(self, data, mode="normal"):
        own = self.getOwnId()
        timetable = []
        for day in data:
            timetable.append([])
            lessons = timetable[-1]
            for lesson in day["gridEntries"]:
                details = self.getLessonDetails(own, lesson["duration"]["start"], lesson["duration"]["end"], mode)
                analyzed = self.analyzeLesson(details)

                merge = True
                if lessons == []:
                    merge = False
                else:
                    keys = ["rooms", "room", "room-info", "subject", "teachers-long", "teachers-short"]
                    for key in keys:
                        if analyzed[key] != lessons[-1][key]:
                            merge = False
                            break
                    if analyzed["start"] != lessons[-1]["end"]: # break betewen
                        if analyzed["start"] != lessons[-1]["start"]:
                            merge = False

                if merge:
                    lessons[-1]["end"] = analyzed["end"]
                    lessons[-1]["endDateTime"] = analyzed["endDateTime"]
                    lessons[-1]["duration"] = lessons[-1]["end"] - lessons[-1]["start"]
                else:
                    lessons.append(analyzed)
        return timetable

    def getOwnId(self):
        return self.getGeneralData()["user"]["person"]["id"]

    def getMyData(self):
        path = "/WebUntis/api/rest/view/v1/timetable/filter?resourceType=STUDENT"
        data = self._getRequest(path)
        print(data)

    def getSchoolYears(self):
        path = "/WebUntis/api/rest/view/v1/schoolyears"
        data = self._getRequest(path)
        return data

    def getGeneralData(self):
        path = "/WebUntis/api/rest/view/v1/app/data"
        data = self._getRequest(path)
        return data

    def getHolidays(self):
        return self.getGeneralData()["holidays"]

    def getHoliday(self, day):
        for holiday in self.getHolidays():
            start = datetime.datetime.strptime(holiday["start"], "%Y-%m-%dT%H:%M:%S")
            end = datetime.datetime.strptime(holiday["end"], "%Y-%m-%dT%H:%M:%S")
            if start <= day <= end:
                holiday["start"] = start
                holiday["end"] = end
                return holiday
        return {
            "start": day,
            "end": day,
            "name": _("No data")
        }

    def getCurrentSchoolYear(self):
        now = datetime.datetime.now()
        years = self.getSchoolYears()
        for year in years:
            start = datetime.datetime.strptime(year["dateRange"]["start"], "%Y-%m-%d")
            end = datetime.datetime.strptime(year["dateRange"]["end"], "%Y-%m-%d")
            if start < now < end:
                return year

    def getAbsences(self, start=None, end=None):
        year = self.getCurrentSchoolYear()
        if start is None:
            start = datetime.datetime.strptime(year["dateRange"]["start"], "%Y-%m-%d")
        if end is None:
            end = datetime.datetime.strptime(year["dateRange"]["end"], "%Y-%m-%d")

        path="/WebUntis/api/classreg/absences/students?startDate=" + start.strftime("%Y%m%d") + "&endDate=" + end.strftime("%Y%m%d") + "&studentId=23225&excuseStatusId=-1"
        data = self._getRequest(path)
        return data["data"]["absences"]

    def getMessages(self):
        path = "/WebUntis/api/rest/view/v1/messages"
        data = self._getRequest(path)
        return data["incomingMessages"]

    def getMessageById(self, id):
        path = "/WebUntis/api/rest/view/v1/messages/" + str(id)
        data = self._getRequest(path)

        if data is None:
            all = self.getMessages()
            for message in all:
                if message["id"] == id:
                    message["content"] = message["contentPreview"]
                    return message
        else:
            return data

    def getTeacherById(self, id):
        path = "/WebUntis/api/rest/view/v1/teachers/" + str(id)
        data = self._getRequest(path)
        return data

    def getLessonDetails(self, id, start, end, mode="normal"):
        path = "/WebUntis/api/rest/view/v2/calendar-entry/detail?elementId=" + str(id) + "&elementType=5&endDateTime=" + end + "&homeworkOption=DUE&startDateTime=" + start
        data = self._getRequest(path, mode)
        data = data["calendarEntries"]

        takingPlace = []
        cancelled = []
        for lesson in data:
            if lesson["status"] == "CANCELLED":
                cancelled.append(lesson)
            else:
                takingPlace.append(lesson)

        if takingPlace != []:
            lesson = takingPlace[0]
            if cancelled != []:
                lesson["original"] = cancelled[0]
        else:
            lesson = cancelled[0]

        return lesson

    def getAllRooms(self):
        year = self.getCurrentSchoolYear()
        start = datetime.datetime.strptime(year["dateRange"]["start"], "%Y-%m-%d")
        end = datetime.datetime.strptime(year["dateRange"]["end"], "%Y-%m-%d")
        path = "/WebUntis/api/rest/view/v1/calendar-entry/rooms/form?endDateTime=" + end.strftime("%Y-%m-%dT%H:%M:%S") + "&startDateTime=" + start.strftime("%Y-%m-%dT%H:%M:%S")
        data = self._getRequest(path)
        return data

    def getHomeworks(self, start=None, end=None):
        year = self.getCurrentSchoolYear()
        if start is None:
            start = datetime.datetime.strptime(year["dateRange"]["start"], "%Y-%m-%d")
        if end is None:
            end = datetime.datetime.strptime(year["dateRange"]["end"], "%Y-%m-%d")

        path="/WebUntis/api/homeworks/lessons?startDate=" + start.strftime("%Y%m%d") + "&endDate=" + end.strftime("%Y%m%d")
        data = self._getRequest(path)
        return data["data"]


