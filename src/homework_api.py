from .api import api
import json
from webuntis.utils.remote import rpc_request
import datetime
import os
from .credentials import getCredentials

CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-hw/"
os.system("mkdir -p " + CACHEDIR)

def writeDay(date, data):
    name = date + "hw"
    print("wrtiting homeworks",date)
    with open(CACHEDIR + name, "w") as file:
        json.dump(data, file)
    api.updateCache(name)

def loadDay(date):
    name = date + "hw"
    print("reading homeworks",date)
    with open(CACHEDIR + name) as file:
        return json.load(file)

def fetchHomeworks(start, end, useCache = False):
    day_count = (end-start).days + 1
    if not useCache:
        useCache = True
        for date in (start + datetime.timedelta(n) for n in range(day_count)):
            if not api.useCacheName(date.strftime("%Y%m%d") + "hw"):
                useCache = False
                break

    if not useCache:
        try:
            session = api.login()

            jsessionid = session.config["jsessionid"]
            useragent = session.config["useragent"]
            server = getCredentials()["server"]
            school = session.config["school"]

            s = session.config["_http_session"]

            url = server + "/WebUntis/api/homeworks/lessons?startDate=" + start.strftime("%Y%m%d") + "&endDate=" + end.strftime("%Y%m%d") + "&school=" + school
            if not url.startswith("https://"):
                url = "https://" + url

            headers = {
                u'User-Agent': useragent,
                u'Content-Type': u'application/json'
            }
            headers['Cookie'] = u'JSESSIONID=' + jsessionid

            r = s.get(url, headers=headers)
            result = json.loads(r.text)

            data = result["data"]
            lessons = data["lessons"]
            homeworks = data["homeworks"]

            days = {}
            for date in (start + datetime.timedelta(n) for n in range(day_count)):
                days[date.strftime("%Y%m%d")] = []

            for homework in homeworks:
                day = str(homework["dueDate"])
                days[day].append(homework)
                for lesson in lessons:
                    if lesson["id"] == homework["lessonId"]:
                        homework["subject"] = lesson["subject"]

            result = []
            for day in days:
                writeDay(day, days[day])
                result += days[day]

            session.logout()

            return result
        except:
            useCache = True
            raise
    if useCache:
        result = []
        for date in (start + datetime.timedelta(n) for n in range(day_count)):
            day = loadDay(date.strftime("%Y%m%d"))
            result += day
        return result
