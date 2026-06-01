import datetime

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


release = "\n    <release version=\"" + version + "\" date=\"" + datetime.date.today().strftime("%Y-%m-%d") + "\">\n      <description translate=\"no\">\n        <ul>"
for new in news:
    release += "\n          <li>" + new + "</li>"
release += "\n        </ul>\n      </description>\n    </release>"


meta = meta[:pos] + release + meta[pos:]


with open("data/page.codeberg.ostfriese4.Untis.metainfo.xml.in", "w") as file:
    file.write(meta)
