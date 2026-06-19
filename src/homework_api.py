import json
import datetime
import os

DATAPATH = os.environ.get("XDG_DATA_HOME", ".untis") + "/homework.json"

shared = None


def setShared(new):
    global shared
    shared = new


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


def fetchHomeworks(start=None, end=None, mode="normal", orig=False):
    data = shared.session.getHomeworks(start, end)
    lessons = data["lessons"]
    homeworks = data["homeworks"]

    result = []

    for homework in homeworks:
        day = str(homework["dueDate"])
        for lesson in lessons:
            if lesson["id"] == homework["lessonId"]:
                homework["subject"] = lesson["subject"]
        if orig:
            result.append(homework)
        else:
            result.append(applyChanges(homework))

    return result


def applyChanges(item):
    if type(item) != dict:
        print(item)
        return
    id = str(item["id"])
    if id in ownData:
        changes = ownData[id]
        item["oldKeys"] = {}
        for key in changes:
            if not id.startswith("own"):
                item["oldKeys"][key] = item[key]
            item[key] = changes[key]
    return item


def getAll(orig=False):
    data = fetchHomeworks(orig=orig)
    for id in ownData:
        if id.startswith("own"):
            data.append(ownData[id])
    return data


def setValue(id, key, value):
    id = str(id)
    if not id in ownData:
        ownData[id] = {"id": id}
    ownData[id][key] = value
    writeOwnData(ownData)


def getById(id, orig=False):
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
        i += 1
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
