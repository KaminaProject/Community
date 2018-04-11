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
basic.py - Class that implements basic commands for managing a -community node
"""

import os
import platform
import tempfile
import shutil
import shlex
import subprocess
import logging
import sys
from pathlib import PurePath

import requests
from tqdm import tqdm

from kamina.process import KaminaProcess


class BasicCommands:
    """Basic commands for managing the -community node."""
    def __init__(self, kamina_process: KaminaProcess):
        self.settings = kamina_process.conf
        self.verbose = self.settings["troubleshoot"]["verbose"]
        self.logger = logging.getLogger("kamina")

    def setup_community_node(self, install_ipfs: bool) -> None:
        """
        Setup a new kamina-community node
        :param install_ipfs: Whether to download ipfs using this script
        :return: None
        """
        community_dir_path = self.settings["general"]["node_dir"]
        ipfs_init_command = ["IPFS_PATH=%s" % shlex.quote(community_dir_path), "ipfs", "init"]
        self.logger.info("Setting up a new community node in %s" % community_dir_path)

        # Try to create the folder in which kamina-community will reside
        try:
            os.makedirs(community_dir_path)
        except OSError:
            pass

        # Try to initilize the community dir path
        if not install_ipfs:
            if self.verbose:
                return_code = subprocess.run(" ".join(ipfs_init_command),
                                             shell=True).returncode
            else:
                return_code = subprocess.run(" ".join(ipfs_init_command),
                                             shell=True, stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL).returncode
            if return_code == 127:  # Command not found
                self.logger.error("It looks like ipfs is not in your PATH, "
                                  "add flag --install-ipfs to install ipfs locally.")
                sys.exit(1)

            elif return_code == 1:  # ipfs node alredy exists
                self.logger.error("Community node already "
                                  "initialized in '%s'" % community_dir_path)
                sys.exit(1)
        else:
            self.logger.debug("Downloading ipfs for current platform")
            # Only download if the folder go-ipfs doesnt exist already
            install_dir = str(PurePath(self.settings["storage"]["ipfs"]["install_dir"]))
            if not os.path.exists(install_dir):
                self.__install_ipfs(install_dir)
            else:
                self.logger.error("Directory '%s' already exists, "
                                  "aborting download" % install_dir)
                sys.exit(1)

            # Now initialize the ipfs node with the downloaded binary
            ipfs_init_command[1] = shlex.quote(str(PurePath(
                self.settings["storage"]["ipfs"]["install_dir"],
                "ipfs"
            )))
            if self.verbose:
                return_code = subprocess.run(" ".join(ipfs_init_command),
                                             shell=True).returncode
            else:
                return_code = subprocess.run(" ".join(ipfs_init_command),
                                             shell=True, stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL).returncode
            if return_code == 1:  # ipfs node alredy exists
                self.logger.error("Community node already "
                                  "initialized in '%s'" % community_dir_path)
                sys.exit(1)

        # Print friendly message if everything went all right
        self.logger.info("Finished setting up kamina-community node.")

    def __install_ipfs(self, install_dir: str) -> None:
        """
        Download the correct ipfs binary for your platform
        :return: None
        """
        # Download to a temporary directory
        system = platform.system()
        arch = platform.machine()
        extension = "tar.gz"

        # Replace the system name
        if system == "Linux":
            system = "linux"
        elif system == "Windows":
            system = "windows"
            extension = "zip"  # The windows binary uses another extension

        # Replace the arch
        if arch == "x86_64":
            arch = "amd64"
        elif arch == "i386":
            arch = "386"

        temp_dl_dir = tempfile.TemporaryDirectory()
        temp_dl_filename = "go-ipfs_v0.4.14_%s-%s.%s" % (system, arch, extension)
        temp_dl_file_location = str(PurePath(temp_dl_dir.name, temp_dl_filename))
        download_url = "https://dist.ipfs.io/go-ipfs/v0.4.14/%s" % temp_dl_filename
        # Now download the file
        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        with open(temp_dl_file_location, "wb") as file:
            if self.verbose:
                # Show a nice progress bar
                pbar = tqdm(total=total_size, unit="B", unit_scale=True)
                for data in response.iter_content(1024):
                    file.write(data)
                    pbar.update(1024)
                pbar.close()
            else:
                for data in response.iter_content():
                    file.write(data)

        # Extract it
        self.logger.debug("Extracting downloaded binary...")
        shutil.unpack_archive(temp_dl_file_location, temp_dl_dir.name)
        self.logger.debug("Copying files to '%s'..." % install_dir)
        shutil.copytree(str(PurePath(temp_dl_dir.name, "go-ipfs")), install_dir)
