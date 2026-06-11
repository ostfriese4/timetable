import json
import datetime
import os

CACHEDIR = os.environ.get("XDG_CACHE_HOME", ".untis") + "/untis-hw/"
DATAPATH = os.environ.get("XDG_DATA_HOME", ".untis") + "/homework.json"

session = None
def setSession(new):
    global session
    session = new

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

def fetchHomeworks(start, end, mode = "normal"):
    day_count = (end-start).days + 1
    data = session.getHomeworks(start, end)
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

def getAll(orig = False):
    data = []
    for day in os.listdir(CACHEDIR):
        with open(CACHEDIR + day) as file:
            dayData = json.load(file)
            for item in dayData:
                if orig:
                    data.append(item)
                else:
                    data.append(applyChanges(item))
    for id in ownData:
        if id.startswith("own"):
            data.append(ownData[id])
    return data

def setValue(id,key,value):
    id = str(id)
    if not id in ownData:
        ownData[id] = {"id": id}
    ownData[id][key] = value
    writeOwnData(ownData)

def getById(id, orig = False):
    id = str(id)
    for item in getAll(orig):
        if str(item["id"]) == id:
            return item

def delete(id):
    id = str(id)
    if id in ownData:
        del ownData[id]
        writeOwnData(ownData)

def getNewId():
    i = 0
    while "own" + str(i) in ownData:
        i+=1
    return "own" + str(i)

def getChanges(id):
    id = str(id)
    if id.startswith("own"):
        return {}
    elif id in ownData:
        orig = getById(id, True)
        out = {}
        for key in ownData[id]:
            if key != "id":
                old = orig[key]
                new = ownData[id][key]
                if old != new:
                    out[key] = (old, new)
        return out
    return {}
