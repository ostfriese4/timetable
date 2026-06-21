import gi

gi.require_version("Secret", "1")

from gi.repository import Secret
import json
import os

credentialsPath = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"

SCHEMA = Secret.Schema.new(
    "page.codeberg.ostfriese4.Untis.Store",
    Secret.SchemaFlags.NONE,
    {
        "server": Secret.SchemaAttributeType.STRING,
        "school": Secret.SchemaAttributeType.STRING,
        "user": Secret.SchemaAttributeType.STRING,
        "type": Secret.SchemaAttributeType.STRING,
    },
)

def getCredentialsFile():
    try:
        with open(credentialsPath) as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "profiles":        {},
            "credentials":     {},
            "default-profile": None
        }

def setCredentials(server, school, user, password, credType, profile="1"):
    data = getCredentialsFile()

    if not "default-profile" in data:
        data["default-profile"] = profile
    if not "credentials" in data:
        data["credentials"] = {}
    if not "profiles" in data:
        data["profiles"] = {}
    if not profile in data["profiles"]:
        data["profiles"][profile] = {"name": _("Profile") + " " + profile}

    data["credentials"][profile] = {
        "user": user,
        "server": server,
        "school": school,
        "type": credType,
    }

    with open(credentialsPath, "w") as file:
        json.dump(data, file, indent=4)
    Secret.password_store_sync(
        SCHEMA,
        data["credentials"][profile],
        Secret.COLLECTION_DEFAULT,
        "Untis Password",
        password,
        None,
    )


def getPassword(user):
    password = Secret.password_lookup_sync(SCHEMA, user, None)
    if password == None:
        raise FileNotFoundError("no password set")
    return password


def getCredentials(profile="1"):
    data = getCredentialsFile()

    if "password" in data:  # not yet migrated to secrets
        print("migrating password to secrets")
        setCredentials(
            data["server"], data["school"], data["username"], data["password"]
        )
        return getCredentials()

    if not "default-profile" in data:  # not yet migrated to profiles
        print("migrating password to profiles")
        with open(credentialsPath, "w") as file:
            json.dump({}, file)
        setCredentials(
            data["server"],
            data["school"],
            data["user"],
            getPassword(data),
            "password",
            profile,
        )
        return getCredentials()

    if not profile in data["credentials"]:
        raise FileNotFoundError("no password set")

    data = data["credentials"][profile]
    data["password"] = getPassword(data)
    data["profile"] = profile

    if not data["server"].startswith("https://"):
        data["server"] = "https://" + data["server"]
    return data


def getProfiles():
    data = getCredentialsFile()
    try:
        return {
            "profiles": data["profiles"],
            "default-profile": data["default-profile"],
        }
    except:
        getCredentials()  # not migrated
        return getProfiles()


def setProfiles(new):
    data = getCredentialsFile()
    data["profiles"] = new["profiles"]
    data["default-profile"] = new["default-profile"]
    with open(credentialsPath, "w") as file:
        json.dump(data, file, indent=4)
