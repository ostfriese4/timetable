import gi
gi.require_version('Secret', '1')

from gi.repository import Secret
import json
import os

credentialsPath = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"

SCHEMA = Secret.Schema.new("page.codeberg.ostfriese4.Untis.Store",
    Secret.SchemaFlags.NONE,
    {
        "server": Secret.SchemaAttributeType.STRING,
        "school": Secret.SchemaAttributeType.STRING,
        "user": Secret.SchemaAttributeType.STRING
    }
)

def setCredentials(server, school, user, password, profile = "0"):
    try:
        with open(credentialsPath) as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    if not "default-profile" in data:
        data["default-profile"] = profile

    data[profile] = {
            "user": user,
            "server": server,
            "school": school
           }

    with open(credentialsPath, "w") as file:
        json.dump(data, file, indent = 4)
    Secret.password_store_sync(SCHEMA, data[profile], Secret.COLLECTION_DEFAULT, "Untis Password", password, None)

def getPassword(user):
    password = Secret.password_lookup_sync(SCHEMA, user, None)
    if password == None:
        raise FileNotFoundError("no password set")
    return password

def getCredentials(profile = "0"):
    with open(credentialsPath) as file:
        data = json.load(file)

    if "password" in data: # not yet migrated to secrets
        print("migrating password to secrets")
        setCredentials(data["server"], data["school"], data["username"], data["password"])
        return getCredentials()

    if not "default-profile" in data: # not yet migrated to profiles
        print("migrating password to profiles")
        with open(credentialsPath, "w") as file:
            json.dump({}, file)
        setCredentials(data["server"], data["school"], data["user"], getPassword(data), profile)
        return getCredentials()

    data = data[profile]
    data["password"] = getPassword(data)

    if not data["server"].startswith("https://"):
        data["server"] = "https://" + data["server"]
    return data
