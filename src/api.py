import datetime
import json
import os
import webuntis

session = None

def getJSONTimetable(start, end):
    table = session.my_timetable(start=monday, end=friday).to_table()

    json = []

def login():
    global session

    credentials = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"
    with open(credentials) as file:
        credentials = json.load(file)
        session = webuntis.Session(
            username=credentials["username"],
            password=credentials["password"],
            server=credentials["server"],
            school=credentials["school"],
            useragent='WebUntis Test'
            )
        session.login()

def logout():
    session.logout()


def test():
    login()
    for klasse in session.klassen():
        print(klasse.name)
    monday = datetime.date(2026, 3, 2)
    friday = datetime.date(2026, 3, 6)
    table = session.my_timetable(start=monday, end=friday).to_table()
    print(table)
    logout()
