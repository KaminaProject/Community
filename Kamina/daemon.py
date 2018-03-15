import subprocess
import os
import platform
import tempfile
import shutil
import shlex
import threading
from pathlib import Path, PurePath

import requests
from tqdm import tqdm

"""
Kamina.daemon.py - Process and Thread handlers for backgrounded Kamina instances
Provides a python class for maintaining some consistent state across processes
and threads.
"""

"""
Kamina - The />p/ social network
Copyright (C) 2018, The Kamina Project

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

class KaminaInstance:
    """Class providing state for the Kamina daemon"""

    # Not providing any defaults here, as an instance needs at least some conf
    # and a logger to speak out to.
    def __init__(self, conf, logger) -> None:
        self.running = False
        self.lock = threading.Lock()

        # Like I said, we need at least some basic conf and a logger
        if not logger:
            print("KaminaInstance:  not given a valid logger.")
            raise Exception
        else:
            self.logger = logger
        if ("debug" not in conf) or ("verbose" not in conf):
            print("KaminaInstance:  not given valid conf.")
            raise Exception
        else:
            self.debug = conf["debug"]
            self.verbose = conf["verbose"]


def setup(kaminainstance_handle, download_ipfs) -> None:
    """Called to initialize a new Kamina instance"""
    handle = kaminainstance_handle
    community_dir_path = str(PurePath(Path.home(), ".kamina-frontend"))

    # Try to create the folder ${HOME}/.kamina-backend
    try:
        os.makedirs(community_dir_path)
    except OSError:
        pass

    # Check if the directory is empty
    # We should really check if the node has already been initialized
    if os.listdir(community_dir_path):
        print("Folder '%s' is not empty!" % community_dir_path)

    # Check if ipfs is in the path
    try:
        subprocess.run(["ipfs"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        if not download_ipfs:
            print("It looks like ipfs is not in your PATH, "
                  "add flag --download-ipfs to download IPFS through this script")
            handle.running = False
            return

    # Only download if the folder go-ipfs doesnt exist already
    if download_ipfs and not os.path.exists(str(PurePath(community_dir_path, "go-ipfs"))):
        print("IPFS not located, downloading IPFS binary for your platform...")
        # Download to a temporary directory
        extract_dir = str(PurePath(community_dir_path))
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
        temp_dl_file_location = str(PurePath(temp_dl_dir.name, "ipfs-bin.%s" % extension))
        download_url = "https://dist.ipfs.io/go-ipfs/v0.4.13/go-ipfs_v0.4.13_%s-%s.%s" \
                       % (system, arch, extension)
        response = requests.get(download_url, stream=True)
        # TODO: Improve the size
        with open(temp_dl_file_location, "wb") as handler:
            for data in tqdm(response.iter_content(chunk_size=1024), unit_scale=True):
                handler.write(data)

        # Now extract the temporary file
        print("Extracting downloaded binary...")
        shutil.unpack_archive(temp_dl_file_location, extract_dir)

    # Now initialize the ipfs node
    binary_location = "ipfs"  # >implying ipfs is in the PATH
    if download_ipfs:
        binary_location = str(PurePath(community_dir_path, "go-ipfs", "ipfs"))
    ipfs_node_path = shlex.quote(community_dir_path)  # Just to be sure
    ipfs_init_command = "IPFS_PATH=%s %s init" % (ipfs_node_path, binary_location)
    try:
        subprocess.run(ipfs_init_command, shell=True)
    except FileNotFoundError:
        print("Unable to initialize ipfs node, ipfs binary not found.")
        handle.running = False
        return

    handle.running = False
