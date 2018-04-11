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
import urllib.request
import urllib.error
from pathlib import PurePath

import ipfsapi

from core.kamina import KaminaProcess


class AdvancedCommands:
    """Manage advanced cli commands"""
    def __init__(self, kamina_process: KaminaProcess):
        self.settings = kamina_process.conf
        self.logger = logging.getLogger("kamina")
        self.verbose = self.settings.get("verbose")
        self.process = kamina_process

    def _get_ipfs_bin_path(self) -> str:
        """
        Find the location of the ipfs binary
        :return: The location of ipfs binary, otherwise, FileNotFoundError
        """
        local_ipfs_dir = self.settings["local_ipfs_install"]["directory"]
        bin_path = "ipfs"
        ipfs_in_path = True

        try:
            subprocess.run([bin_path], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            self.logger.debug("IPFS is not in your path, trying to use local ipfs instead")
            ipfs_in_path = False

        if not ipfs_in_path:
            try:
                subprocess.run([str(PurePath(local_ipfs_dir, "ipfs"))], stdout=subprocess.DEVNULL)
            except FileNotFoundError:
                raise FileNotFoundError
            else:
                bin_path = str(PurePath(local_ipfs_dir, "ipfs"))

        return bin_path

    def _ipfs_process(self, ipfs_command: str):
        """
        Wrapper function for ipfs daemon initialization
        """
        self.logger.debug("Starting ipfs thread")
        ipfs_running = False
        process = None
        while self.process.running:
            time.sleep(0.01)
            if not ipfs_running:
                ipfs_running = True
                if self.verbose:
                    process = subprocess.Popen(ipfs_command, shell=True)
                else:
                    process = subprocess.Popen(ipfs_command, shell=True,
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL)
        self.logger.debug("Stopping ipfs thread")
        process.terminate()

    def _flask_process(self):
        self.logger.debug("Starting api thread")

    def start_community_daemon(self):
        """
        Starts both the flask api server and the ipfs daemon server
        In charge of handling some end signals
        :return: Nothing
        """
        self.logger.info("Starting community daemon...")
        try:
            ipfs_binary = self._get_ipfs_bin_path()
        except FileNotFoundError:
            self.logger.exception("Unable to locate IPFS, aborting")
            sys.exit(1)
        community_dir_path = shlex.quote(self.settings["general_information"]["node_directory"])
        ipfs_command = "IPFS_PATH=%s %s daemon" % (community_dir_path, ipfs_binary)
        # Flags for thread control
        ipfs_started = False
        flask_started = False
        all_good = False

        # Setup threads
        ipfs_thread = threading.Thread(
            target=self._ipfs_process,
            args=(ipfs_command,)
        )

        flask_thread = threading.Thread(
            target=self.backend.app.run,
            kwargs={"port": 1337}
        )

        # For now, looks like the only way to achieve propper multithreading with flask
        flask_thread.setDaemon(True)

        while self.process.running:
            time.sleep(0.01)  # Avoid 100% CPU usage
            # This way we start threads only once
            if not ipfs_started:
                ipfs_started = True
                ipfs_thread.start()

            if not flask_started:
                flask_started = True
                flask_thread.start()

            if not all_good:
                # Check if the ipfs daemon finished starting
                try:
                    ipfsapi.connect('127.0.0.1', 5001)  # TODO: Add port configuration functionality
                except ipfsapi.exceptions.ConnectionError:
                    continue
                # Check if flask finished starting
                try:
                    with urllib.request.urlopen("http://127.0.0.1:1337/api/") as response:
                        if response.code != 200:
                            continue
                except urllib.error.URLError:
                    continue
                # If we reach this point, everything went fine
                all_good = True
                self.logger.info("Community daemon started")
                self.logger.info("- Flask listening on port 1337")
                self.logger.info("- IPFS listening on port 5001")

        ipfs_thread.join()
        self.logger.info("Stopped community daemon")
