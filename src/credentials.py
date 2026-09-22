import gi

gi.require_version("Secret", "1")

from gi.repository import GLib, Secret
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
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    if not "profiles" in data:
        data["profiles"] = {}
    if not "credentials" in data:
        data["credentials"] = {}
    if not "default-profile" in data:
        data["default-profile"] = "0"
    return data

def save(data):
    with open(credentialsPath, "w") as file:
        json.dump(data, file, indent = 4)

def storePassword(attributes, password):
    # returns False if the keyring is unavailable, e.g. when running
    # sandboxed and the host has no working Secret portal implementation
    try:
        Secret.password_store_sync(
            SCHEMA,
            attributes,
            Secret.COLLECTION_DEFAULT,
            "Untis Password",
            password,
            None,
        )
        return True
    except GLib.GError as error:
        print("storing password in the keyring failed:", error.message)
        return False

def setCredentials(server, school, user, password, credType, profile="1"):
    data = getCredentialsFile()

    if data.get("default-profile") is None:
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

    if not storePassword(data["credentials"][profile], password):
        # fall back to the credentials file so logging in still works
        data["credentials"][profile]["password"] = password

    save(data)


def getPassword(attributes):
    # returns the password, "" if none is stored
    # or None if the keyring is unavailable
    try:
        password = Secret.password_lookup_sync(SCHEMA, attributes, None)
    except GLib.GError as error:
        print("reading password from the keyring failed:", error.message)
        return None
    if password == None:
        return ""
    return password


def getCredentials(profile="1"):
    file = getCredentialsFile()

    if not profile in file["credentials"]:
        file["profiles"][profile] = {"name": _("Profile") + " " + profile}
        file["credentials"][profile] = {
            "server":  "",
            "user":    "",
            "school":  "",
            "type":    "password",
        }
        save(file)

    data = file["credentials"][profile]

    if not "password" in data:
        data["password"] = getPassword(data)

    data["profile"] = profile

    if not data["server"].startswith("https://"):
        data["server"] = "https://" + data["server"]
    return data


def getProfiles():
    data = getCredentialsFile()
    return {
        "profiles": data["profiles"],
        "default-profile": data["default-profile"],
    }


def setProfiles(new):
    data = getCredentialsFile()
    data["profiles"] = new["profiles"]
    data["default-profile"] = new["default-profile"]

    for profile in data["credentials"].copy():
        if profile not in data["profiles"]:
            print("deleting credentials of profile", profile)
            del data["credentials"][profile]

    save(data)
