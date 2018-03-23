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

import logging

import backend
from .cmd import Command


class AdvancedCommands(Command):
    def __init__(self, settings):
        super().__init__(settings)
        self.backend = backend.API()

    def start_community_daemon(self):
        # Replace flask's logger with our own logger
        flask_log = logging.getLogger("werkzeug")
        flask_log.setLevel(logging.DEBUG)
        # self.print_info("Starting community daemon...")
        # self.print_verbose("Starting api server on http://localhost:1337/api/")
        self.backend.run(port=1337, debug=True)
        # if self.verbose:
        #     self.backend.app.run(port=1337, debug=True)
        # else:
        #     self.backend.app.run(port=1337)
