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
cli_commands.py: Class containing the command line commands - ipfs version
"""

from core.instance import KaminaInstance
from core.ipfs.basic_commands import BasicCommands
from core.ipfs.advanced_commands import AdvancedCommands
from utils.logger import Logger


class CliCommands:
    """Cli commands for managing the community node"""
    def __init__(self, settings: dict):
        self.settings = settings
        self.verbose = settings["verbose"]
        self.logger = None
        self.basic_cmd = None
        self.adv_cmd = None

    def register_instance(self, instance: KaminaInstance):
        self.logger = Logger(instance)
        self.basic_cmd = BasicCommands(self.settings, self.logger)
        self.adv_cmd = AdvancedCommands(self.settings, self.logger)

    def init(self, install_ipfs: bool):
        self.basic_cmd.setup_community_node(install_ipfs)

    def daemon(self):
        self.adv_cmd.start_community_daemon()
