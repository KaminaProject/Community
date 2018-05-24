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

"""
storage.py - Manage data storage, be it sqlite or ipfs
"""

import importlib
import logging


class Storage:
    """
    Helper class to simplify storage
    """
    def __init__(self, settings: dict):
        self.settings = settings
        self.logger = logging.getLogger("kamina")
        if not settings["storage"]["ipfs"]["enable"]:
            module = importlib.import_module("storage.non-ipfs.engine")
        else:
            module = importlib.import_module("storage.ipfs.engine")
        self.engine = module.Engine(settings)

