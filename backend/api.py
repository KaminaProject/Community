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

from backend.storage.storage import Storage


class API:
    app = Flask(__name__)

    def __init__(self, settings: dict):
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
            },
            {
                "r": "/api/make_post",
                "m": ["POST"],
                "f": self.make_post
            },
            {
                "r": "/api/make_response",
                "m": ["POST"],
                "f": self.make_response
            },
            {
                "r": "/api/get_single_thread",
                "m": ["GET"],
                "f": self.get_single_thread
            },
            {
                "r": "/api/get_all_threads",
                "m": ["GET"],
                "f": self.get_all_threads
            }
        ]

        for route in routes:
            self.add_route(route)

        self.storage = Storage(settings)

    def add_route(self, route):
        self.app.add_url_rule(route["r"], view_func=route["f"], methods=route["m"])

    @staticmethod
    def index():
        return "Hello there!\n"

    def make_post(self):
        pass

    def make_response(self):
        pass

    def get_all_threads(self):
        pass

    def get_single_thread(self):
        pass
