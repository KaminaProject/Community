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

import shlex
import signal
import subprocess
import logging
import sys
import os
import time
import urllib.request
import urllib.error
from pathlib import PurePath

import ipfsapi

from kamina.process import KaminaProcess


class AdvancedCommands:
    """Manage advanced cli commands"""
    def __init__(self, kamina_process: KaminaProcess):
        self.settings = kamina_process.conf
        self.logger = logging.getLogger("kamina")
        self.verbose = self.settings["troubleshoot"]["verbose"]
        self.process = kamina_process

    def _get_ipfs_bin_path(self) -> str:
        """
        Find the location of the ipfs binary
        :return: The location of ipfs binary, otherwise, FileNotFoundError
        """
        local_ipfs_dir = self.settings["ipfs"]["install_dir"]
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

    def _start_ipfs_daemon(self, node_dir: str, ipfs_binary: str) -> subprocess.Popen:
        """
        Wrapper function for ipfs daemon initialization
        """
        self.logger.debug("Starting ipfs daemon...")
        ipfs_env = os.environ.copy()
        ipfs_env["IPFS_PATH"] = node_dir
        ipfs_command = "%s daemon" % ipfs_binary
        if self.verbose:
            ipfs_process = subprocess.Popen(
                ipfs_command.split(),
                env=ipfs_env,
                preexec_fn=os.setpgrp
            )
        else:
            ipfs_process = subprocess.Popen(
                ipfs_command.split(),
                env=ipfs_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setpgrp
            )
        return ipfs_process

    def _start_api_server(self) -> subprocess.Popen:
        self.logger.debug("Starting api server...")
        uwsgi_command = "uwsgi -y conf/uwsgi.yaml"
        if self.verbose:
            uwsgi_process = subprocess.Popen(
                uwsgi_command.split(),
                preexec_fn=os.setpgrp
            )
        else:
            uwsgi_process = subprocess.Popen(
                uwsgi_command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setpgrp
            )
        return uwsgi_process

    def start_community_daemon(self):
        """
        Starts both the flask api server and the ipfs daemon server
        In charge of handling some end signals
        """
        self.logger.info("Starting community daemon...")
        # Setup signal handlers
        self.process.setup_sighandlers()
        try:
            ipfs_binary = self._get_ipfs_bin_path()
        except FileNotFoundError:
            self.logger.exception("Unable to locate IPFS, aborting")
            sys.exit(1)

        community_dir_path = shlex.quote(self.settings["general"]["node_dir"])
        # Flags for process control
        ipfs_started = False
        api_started = False
        all_good = False

        # Variables in order to terminate processes
        ipfs_process = None
        api_process = None

        while self.process.running:
            # This way we start processes only once
            if not ipfs_started:
                ipfs_process = self._start_ipfs_daemon(community_dir_path, ipfs_binary)
                # Wait for ipfs to start
                while not ipfs_started:
                    try:
                        # TODO: Add port configuration functionality
                        ipfsapi.connect('127.0.0.1', 5001)
                    except ipfsapi.exceptions.ConnectionError:
                        continue
                    else:
                        ipfs_started = True
                    time.sleep(0.01)

            if not api_started:
                api_process = self._start_api_server()
                # Wait for uwsgi to start
                while not api_started:
                    try:
                        with urllib.request.urlopen("http://127.0.0.1:1337/api/") as response:
                            if response.code != 200:
                                continue
                    except urllib.error.URLError:
                        continue
                    else:
                        api_started = True
                    time.sleep(0.01)

            if not all_good:
                # If we reach this point, everything went fine
                all_good = True
                self.logger.info("Community daemon started")
                self.logger.info("- Flask listening on port 1337")
                self.logger.info("- IPFS listening on port 5001")

            time.sleep(0.01)  # Avoid 100% CPU usage

        # Now send end signal to all processes
        self.logger.debug("Stopping ipfs daemon...")
        ipfs_process.terminate()
        ipfs_process.wait()
        self.logger.debug("Stopping api server...")
        api_process.send_signal(signal.SIGQUIT)
        api_process.wait()
        self.logger.info("Stopped community daemon")
