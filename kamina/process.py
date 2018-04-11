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
kamina.py - Process and Thread handlers for backgrounded Kamina instances
Provides a python class for maintaining some consistent state across processes
and threads.
"""

import signal
import logging


class KaminaProcess:
    """Class providing state for the Kamina daemon"""

    # Not providing any defaults here, as an instance needs at least some conf
    # and a logger to speak out to.
    def __init__(self, conf: dict) -> None:
        self.running = True
        self.conf = conf
        self.logger = logging.getLogger("kamina")

        # Set up some signal handlers
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGHUP, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.logger.info("Received interrupt signal, shutting down...")
        self.running = False
