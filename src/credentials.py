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
            return json.load(file)
    except FileNotFoundError:
        return {
            "profiles":        {},
            "credentials":     {},
            "default-profile": None
        }

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

    if not storePassword(data["credentials"][profile], password):
        # fall back to the credentials file so logging in still works
        data["credentials"][profile]["password"] = password

    with open(credentialsPath, "w") as file:
        json.dump(data, file, indent=4)


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
    data = getCredentialsFile()

    if "password" in data:  # not yet migrated to secrets
        print("migrating password to secrets")
        setCredentials(
            data["server"], data["school"], data["username"], data["password"], "password"
        )
        return getCredentials()

    if not "default-profile" in data:  # not yet migrated to profiles
        print("migrating password to profiles")
        password = getPassword(data)
        if password is None:  # keyring unavailable, retry on the next run
            raise FileNotFoundError("no password set")
        with open(credentialsPath, "w") as file:
            json.dump({}, file)
        setCredentials(
            data["server"],
            data["school"],
            data["user"],
            password,
            "password",
            profile,
        )
        return getCredentials()

    if not profile in data["credentials"]:
        raise FileNotFoundError("no password set")

    data = data["credentials"][profile]
    fallbackPassword = data.pop("password", "")
    password = getPassword(data)
    if not password:  # not in the keyring or keyring unavailable
        password = fallbackPassword
    data["password"] = password
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
    except KeyError:
        try:
            getCredentials()  # not migrated
        except FileNotFoundError:
            return {"profiles": {}, "default-profile": None}
        return getProfiles()


def setProfiles(new):
    data = getCredentialsFile()
    data["profiles"] = new["profiles"]
    data["default-profile"] = new["default-profile"]
    with open(credentialsPath, "w") as file:
        json.dump(data, file, indent=4)
