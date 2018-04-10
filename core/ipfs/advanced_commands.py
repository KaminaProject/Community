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
advanced_commands.py - Class containing advanced command line commands
"""

import threading
import shlex
import subprocess
import logging
import sys
import time
from pathlib import PurePath

from backend.api import API
from core.kamina import KaminaProcess


# TODO: Fix logging with flask
class AdvancedCommands:
    """Manage advanced cli commands"""
    def __init__(self, kamina_process: KaminaProcess):
        self.settings = kamina_process.conf
        self.backend = API(self.settings)
        self.logger = logging.getLogger("kamina")
        self.verbose = self.settings.get("verbose")
        self.process = kamina_process

    def __get_ipfs_bin_path(self):
        local_ipfs_dir = self.settings["local_ipfs_install"]["directory"]
        bin_path = "ipfs"
        ipfs_in_path = True

        try:
            subprocess.run([bin_path], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            self.logger.info("IPFS is not in your path, trying to use local ipfs instead")
            ipfs_in_path = False

        if not ipfs_in_path:
            try:
                subprocess.run([str(PurePath(local_ipfs_dir, "ipfs"))], stdout=subprocess.DEVNULL)
            except FileNotFoundError:
                raise FileNotFoundError
            else:
                bin_path = str(PurePath(local_ipfs_dir, "ipfs"))

        return bin_path

    def ipfs_process(self, run_event: threading.Event):
        self.logger.info("Starting community daemon in http://localhost:1337/api")
        community_dir_path = shlex.quote(self.settings["general_information"]["node_directory"])

        try:
            ipfs_binary = self.__get_ipfs_bin_path()
        except FileNotFoundError:
            self.logger.exception("Unable to locate IPFS, aborting")
            sys.exit(1)

        ipfs_command = "IPFS_PATH=%s %s daemon" % (community_dir_path, ipfs_binary)
        ipfs_named_args = {
            "shell": True
        }

        if not self.verbose:
            ipfs_named_args["stdout"] = subprocess.DEVNULL

        ipfs_running = False

        while run_event.isSet():
            if not ipfs_running:
                ipfs_running = True
                subprocess.run(ipfs_command, shell=True)

    def flask_process(self, run_event: threading.Event):
        flask_running = False
        while run_event.isSet():
            if not flask_running:
                flask_running = True
                self.backend.app.run(port=1337)

    def start_community_daemon(self):
        run_event = threading.Event()
        run_event.set()
        ipfs_started = False
        flask_started = False

        ipfs_thread = threading.Thread(
            target=self.ipfs_process,
            args=(run_event,)
        )

        api_thread = threading.Thread(
            target=self.flask_process,
            args=(run_event,)
        )

        while True:
            time.sleep(0.01)  # Avoid 100% CPU usage
            if self.process.kill_now:
                ipfs_thread.join()
                api_thread.join()
                run_event.clear()
                break

            if not ipfs_started:
                ipfs_started = True
                ipfs_thread.start()

            if not flask_started:
                flask_started = True
                api_thread.start()
