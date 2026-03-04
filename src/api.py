# api.py
#
# Copyright 2026 Jonas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import json
import os
import webuntis

class untisApi:
    def __init__(self):
        self.session = None

    def getTimetable(self, start, end):
        table = self.session.my_timetable(start=start, end=end).to_table()

        return table

    def login(self):
        credentials = os.environ.get("XDG_DATA_HOME", ".untis/data") + "/credentials.json"
        with open(credentials) as file:
            credentials = json.load(file)
            self.session = webuntis.Session(
                username=credentials["username"],
                password=credentials["password"],
                server=credentials["server"],
                school=credentials["school"],
                useragent='WebUntis Test'
                )
            self.session.login()

    def logout(self):
        self.session.logout()


    def test(self):
        self.login()
        for klasse in self.session.klassen():
            print(klasse.name)
        monday = datetime.date(2026, 3, 2)
        friday = datetime.date(2026, 3, 6)
        table = self.session.my_timetable(start=monday, end=friday).to_table()
        print(table)
        self.logout()

api = untisApi()
