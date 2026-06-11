import requests
import os
import json
import time
import datetime
from pathlib import Path
from .credentials import getCredentials
from hashlib import md5

version = "3.1"
id = "page.codeberg.ostfriese4.Untis"
useragent = id + " " + version

headers = {
    "User-Agent": useragent
}

def _login(credentials):
    s = requests.Session()
    s.headers.update(headers)
    s.headers.update({"Referer": credentials["server"] + "/"})

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
        return s
    else:
        print(response)

class session:
    def __init__(self, credentials = None):
        if credentials is None:
            credentials = getCredentials()
        self.session = _login(credentials)
        self.server = credentials["server"]

        self.name = credentials["school"] + credentials["user"]
        self.name = md5(self.name.encode()).hexdigest()
        self.CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis/" + self.name + "/"
        if not os.path.exists(self.CACHEDIR + "requests"):
            os.makedirs(self.CACHEDIR + "requests")

        self._readCacheIndex()

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

    def _readFromCache(self, object):
        with open(self.CACHEDIR + object) as file:
            return json.load(file)

    def _writeToCache(self, object, content):
        path = self.CACHEDIR + object
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        with open(path, "w") as file:
            json.dump(content, file)
            self.cacheIndex[object] = time.time()
            self._saveCacheIndex()

    def _useCache(self, object, maxage = 3600):
        if object in self.cacheIndex:
            return self.cacheIndex[object] + maxage >= time.time()
        return False

    def _getRequest(self, path, mode = "normal", maxage = 3600):
        if mode == "normal":
            if self._useCache(path, maxage = maxage):
                mode = "cache"
            else:
                mode = "online"
        if mode == "online":
            try:
                response = self.session.get(self.server + path)
                data = response.json()
                if "errorCode" in data:
                    print("ERROR: PATH:", self.server + path, data)
                    mode = "cache"
                else:
                    self._writeToCache("requests/" + md5(path.encode()).hexdigest(), data)
                    return data
            except:
                raise
                mode = "cache"
        if mode == "cache":
            return self._readFromCache("requests/" + md5(path.encode()).hexdigest())

    def getNewsOfDay(self, day = None):
        if day is None:
            day = datetime.date.today()
        path = "/WebUntis/api/public/news/newsWidgetData?date=" + day.strftime("%Y%m%d")
        data = self._getRequest(path)["data"]["messagesOfDay"]
        return data

    def getMyTimetable(self, start, end):
        path = "/WebUntis/api/rest/view/v1/timetable/entries?start=" + start.strftime("%Y-%m-%d") + "&end=" + end.strftime("%Y-%m-%d") + "&format=2&resourceType=STUDENT&timetableType=MY_TIMETABLE&layout=START_TIME"
        data = self._getRequest(path)
        print(data)

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
        print(data)


