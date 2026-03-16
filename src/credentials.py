import json
import os

credentialsPath = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"

def setCredentials(server, school, user, password):
    with open(credentialsPath, "w") as file:
        json.dump({
            "username": user,
            "password": password,
            "server": server,
            "school": school
        },
        file)

def getCredentials():
    with open(credentialsPath) as file:
        return json.load(file)
