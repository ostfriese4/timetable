import datetime
import os

version = input("version: ")

news = []
with open("NEWS", "r") as file:
    for item in file.read().split("\n"):
        if item != "":
            news.append(item)
with open("NEWS", "w") as file:
    file.write("")


description = "        <ul>"
for new in news:
    description += "\n          <li>" + new + "</li>"
description += "\n        </ul>\n"

with open("rn","w") as file:
    file.write(description)
os.system("nano rn")
with open("rn","r") as file:
    description = file.read()
os.system("rm rn")

release = "\n    <release version=\"" + version + "\" date=\"" + datetime.date.today().strftime("%Y-%m-%d") + "\">\n      <description translate=\"no\">\n" + description + "      </description>\n    </release>"


def insertIntoFile(path, before, after, text):
    with open(path, "r") as file:
        content = file.read()
        pos = content.find(before) + len(before)
        fh = content[:pos]
        sh = content[pos:]
        pos = sh.find(after)
        sh = sh[pos:]

        content = fh + text + sh
    with open(path, "w") as file:
        file.write(content)

insertIntoFile("data/page.codeberg.ostfriese4.Untis.metainfo.xml.in", "<releases>", "\n", release)
insertIntoFile("src/api.py", 'version = "', '"', version)
insertIntoFile("src/api.py", 'releaseNotes = "', '"\n', description.replace("\\", "\\\\").replace("\n", "\\n"))
insertIntoFile("README.md", "latest release: ", '">', version)
insertIntoFile("meson.build", "version: '", "',", version)

