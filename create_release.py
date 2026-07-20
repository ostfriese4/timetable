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

with open("src/api.py", "r") as file:
    content = file.read()
    pos = content.find('version = "') + 11
    fh = content[:pos]
    sh = content[pos:]
    pos = sh.find('"')
    sh = sh[pos:]
    content = fh + version + sh
with open("src/api.py", "w") as file:
    file.write(content)

with open("data/page.codeberg.ostfriese4.Untis.metainfo.xml.in") as file:
    meta = file.read()

pos = meta.find("<releases>") + 10

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

release = "\n    <release version=\"" + version + "\" date=\"" + datetime.date.today().strftime("%Y-%m-%d") + "\">      <description translate=\"no\">\n" + description + "\n      </description>\n    </release>"


meta = meta[:pos] + release + meta[pos:]


with open("data/page.codeberg.ostfriese4.Untis.metainfo.xml.in", "w") as file:
    file.write(meta)


with open("src/api.py", "r") as file:
    content = file.read()
    pos = content.find('releaseNotes = "') + 16
    fh = content[:pos]
    sh = content[pos:]
    pos = sh.find('"#""')
    sh = sh[pos:]

    releaseNotes = description.replace("\n", "\\n").replace("\\", "\\\\")

    content = fh + releaseNotes + sh
with open("src/api.py", "w") as file:
    file.write(content)
