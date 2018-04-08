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
import subprocess
import logging
import sys
from multiprocessing import Process
from pathlib import PurePath

from backend.api import API


class AdvancedCommands:
    """Manage advanced cli commands"""
    def __init__(self, settings: dict):
        self.backend = API(settings)
        self.logger = logging.getLogger("kamina")
        self.settings = settings
        self.verbose = settings.get("verbose")

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

    def start_community_daemon(self):
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

        ipfs_thread = Process(
            target=subprocess.run,
            args=(ipfs_command,),
            kwargs=ipfs_named_args
        )

        api_thread = Process(
            target=self.backend.app.run,
            kwargs={"port": 1337}
        )  # TODO: Fix logging with flask

        try:
            self.logger.debug("Starting flask api server")
            api_thread.start()
            self.logger.debug("Starting ipfs daemon")
            ipfs_thread.start()
        except RuntimeError as error:
            self.logger.exception(error)
            self.logger.error("There was an error starting the community daemon")
        except KeyboardInterrupt:
            api_thread.terminate()
            ipfs_thread.terminate()
        else:
            api_thread.join()
            ipfs_thread.join()
