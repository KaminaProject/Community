# Kamina - The />p/ social network
# Copyright (C) 2018, The Kamina Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from flask import Flask


class API:
    app = Flask(__name__)

    def __init__(self):
        # Routes
        routes = [
            {
                "r": "/api",
                "m": ["GET"],
                "f": self.index
            },
            {
                "r": "/api/",
                "m": ["GET"],
                "f": self.index
            }
        ]

        for route in routes:
            self.add_route(route)

    def add_route(self, route):
        self.app.add_url_rule(route["r"], view_func=route["f"], methods=route["m"])

    @staticmethod
    def index():
        return "Hello there!\n"
