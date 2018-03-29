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
import logging
import shlex
import subprocess
from pathlib import PurePath

from utils.logger import Logger
from backend.api import API


class AdvancedCommands():
    """Manage advanced cli commands"""
    def __init__(self, settings: dict, logger: Logger):
        self.backend = API().app
        self.logger = logger
        self.settings = settings
        self.__disable_flask_logger()

    @staticmethod
    def __disable_flask_logger():
        flask_log = logging.getLogger("werkzeug")
        flask_log.setLevel(logging.ERROR)

    def __get_ipfs_bin_path(self):
        local_ipfs_dir = self.settings["local_ipfs_install"]["directory"]
        bin_path = "ipfs"
        ipfs_in_path = True

        try:
            subprocess.run([bin_path], stdout=subprocess.PIPE)
        except FileNotFoundError:
            self.logger.print_verbose("IPFS is not in your path, trying to use local ipfs instead")
            ipfs_in_path = False

        if not ipfs_in_path:
            try:
                subprocess.run([str(PurePath(local_ipfs_dir, "ipfs"))])
            except FileNotFoundError:
                self.logger.print_verbose("IPFS not found in the local install directory")
                raise FileNotFoundError
            else:
                bin_path = str(PurePath(local_ipfs_dir, "ipfs"))

        return bin_path

    def start_community_daemon(self):
        self.logger.print_info("Starting community damon")
        community_dir_path = self.settings["general_information"]["node_directory"]
        try:
            ipfs_binary = self.__get_ipfs_bin_path()
        except FileNotFoundError:
            self.logger.print_error("Unable to locate IPFS, aborting")
        ipfs_command = "IPFS_PATH=%s %s daemon" % (community_dir_path, ipfs_binary)
        api_thread = threading.Thread(
            target=self.backend.run, kwargs={"port":1337})  # TODO: Fix logging with flask
        ipfs_thread = threading.Thread(
            target=subprocess.run, args=(ipfs_command,),
            kwargs={"shell": True})
        try:
            self.logger.print_verbose("Starting flask api server")
            api_thread.start()
            self.logger.print_verbose("Starting ipfs daemon")
            ipfs_thread.start()
            self.logger.print_info("Done starting community daemon, api server listening on"
                                   "http://localhost:1337/api")
        except RuntimeError as error:
            self.logger.print_verbose(error)
            self.logger.print_error("There was an error starting the community daemon")
        else:
            api_thread.join()
            ipfs_thread.join()
