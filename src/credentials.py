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

def setCredentials(server, school, user, password):
    data = {
            "user": user,
            "server": server,
            "school": school
           }
    with open(credentialsPath, "w") as file:
        json.dump(data, file)
    Secret.password_store_sync(SCHEMA, data, Secret.COLLECTION_DEFAULT, "Untis Password", password, None)

def getCredentials():
    with open(credentialsPath) as file:
        data = json.load(file)
    password = Secret.password_lookup_sync(SCHEMA, data, None)
    if password == None:
        if "password" in data: # not yet migrated
            print("migrating password")
            setCredentials(data["server"], data["school"], data["username"], data["password"])
            return getCredentials()
        raise FileNotFoundError("no password set")
    data["password"] = password
    return data
