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

import importlib
import logging


class Storage:
    def __init__(self, settings: dict):
        self.settings = settings
        self.logger = logging.getLogger("kamina")
        if not settings["enable_ipfs"]:
            self.engine = importlib.import_module("backend.storage.non-ipfs.engine").Engine(settings)
        else:
            self.engine = importlib.import_module("backend.storage.ipfs.engine").Engine(settings)

    def make_thread(self):
        pass
