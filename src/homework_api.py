from .api import api
import json
from webuntis.utils.remote import rpc_request
import datetime
import os
import requests
from .credentials import getCredentials

CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-hw/"
DATAPATH = os.environ.get("XDG_DATA_HOME", ".untis") + "/homework.json"

if not os.path.exists(CACHEDIR):
    os.mkdir(CACHEDIR)

def loadOwnData():
    if os.path.exists(DATAPATH):
        with open(DATAPATH) as file:
            return json.load(file)
    else:
        return {}

def writeOwnData(data):
    with open(DATAPATH, "w") as file:
        json.dump(data, file, indent=4)

ownData = loadOwnData()

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
        if not api.testLogin():
            print("login failed")
            return []
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
                for item in days[day]:
                    result.append(applyChanges(item))

            session.logout()

            return result
        except requests.exceptions.ConnectionError:
            useCache = True
    if useCache:
        result = []
        for date in (start + datetime.timedelta(n) for n in range(day_count)):
            day = loadDay(date.strftime("%Y%m%d"))
            for item in day:
                result.append(applyChanges(item))
        return result

def applyChanges(item):
    id = str(item["id"])
    if id in ownData:
        changes = ownData[id]
        item["oldKeys"] = {}
        for key in changes:
            if not id.startswith("own"):
                item["oldKeys"][key] = item[key]
            item[key] = changes[key]
    return item

def getAll():
    data = []
    for day in os.listdir(CACHEDIR):
        with open(CACHEDIR + day) as file:
            dayData = json.load(file)
            for item in dayData:
                data.append(applyChanges(item))
    return data

def setValue(id,key,value):
    id = str(id)
    if not id in ownData:
        ownData[id] = {"id": id}
    ownData[id][key] = value
    writeOwnData(ownData)

def getById(id):
    id = str(id)
    for item in getAll():
        if str(item["id"]) == id:
            return item
