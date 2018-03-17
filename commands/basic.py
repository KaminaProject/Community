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
from pathlib import Path, PurePath

import requests


class BasicCommands:
    """Basic commands for managing the -community node."""
    def __init__(self, context):
        self.verbose = context.obj['CONF']['verbose']

    def verbose_only(self, message: str) -> None:
        """
        Print message only if the --verbose flag was passed
        :param message: The message to be printed
        :return: None
        """
        if self.verbose:
            print(message)

    def install_ipfs(self, extract_dir) -> None:
        """
        Download the correct ipfs binary for your platform
        :return: None
        """
        self.verbose_only("IPFS not located, downloading binary for your platform...")
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

        # Now download the file
        temp_dl_dir = tempfile.TemporaryDirectory()
        temp_dl_filename = "go-ipfs_v0.4.13_%s-%s.%s" % (system, arch, extension)
        temp_dl_file_location = str(PurePath(temp_dl_dir.name, temp_dl_filename))
        download_url = "https://dist.ipfs.io/go-ipfs/v0.4.13/%s" % temp_dl_filename
        response = requests.get(download_url, stream=True)
        with open(temp_dl_file_location, "wb") as handler:
            for data in response.iter_content():
                handler.write(data)

        # Extract it
        self.verbose_only("Extracting downloaded binary...")
        shutil.unpack_archive(temp_dl_file_location, extract_dir)

    def setup_community_node(self, download_ipfs: bool) -> None:
        """
        Setup a new kamina-community node
        :param download_ipfs: Whether to download ipfs using this script
        :return: None
        """
        community_dir_path = str(PurePath(Path.home(), ".kamina-community"))
        # TODO: add the spinner in case --verbose is not passed
        # spinner = itertools.cycle(['-', '/', '|', '\\'])
        # Try to create the folder ${HOME}/.kamina-backend
        try:
            os.makedirs(community_dir_path)
        except OSError:
            pass

        # Check if the directory is empty
        # We should really check if the node has already been initialized
        if os.listdir(community_dir_path):
            self.verbose_only("Folder '%s' is not empty!" % community_dir_path)

        # Check if ipfs is in the path
        try:
            subprocess.run(["ipfs"], stdout=subprocess.PIPE)
        except FileNotFoundError:
            if not download_ipfs:
                raise Exception("It looks like ipfs is not in your PATH, "
                                "add flag --download-ipfs to download IPFS through this script")

        # Only download if the folder go-ipfs doesnt exist already
        if download_ipfs and not os.path.exists(str(PurePath(community_dir_path, "go-ipfs"))):
            self.install_ipfs(community_dir_path)

        # Now initialize the ipfs node
        binary_location = "ipfs"  # >implying ipfs is in the PATH
        if download_ipfs:
            binary_location = str(PurePath(community_dir_path, "go-ipfs", "ipfs"))
        ipfs_init_command = "IPFS_PATH=%s %s init" % \
                            (shlex.quote(community_dir_path), shlex.quote(binary_location))
        try:
            if self.verbose:
                subprocess.run(ipfs_init_command, shell=True)
            else:
                subprocess.run(ipfs_init_command, shell=True, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise Exception("Unable to initialize ipfs node, ipfs binary not found.")

        print("Finished setting up kamina-community node.")
