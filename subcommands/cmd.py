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

import sys

from .utils import error_msg, verbose_msg, info_msg
from kamina import KaminaInstance


class Command:
    def __init__(self, settings: dict):
        self.settings = settings
        self.verbose = settings["verbose"]
        self.instance = None

    def append_to_instance(self, instance: KaminaInstance) -> None:
        self.instance = instance

    def print_verbose(self, message: str) -> None:
        """
        Print a message only if the --verbose flag was passed
        :param message: The message to be printed
        :return: None
        """
        if self.verbose:
            self.instance.logger.info(verbose_msg() + message)

    def print_error(self, message: str) -> None:
        self.instance.logger.error(error_msg() + message)
        self.end_execution()

    def print_info(self, message: str) -> None:
        self.instance.logger.info(info_msg() + message)

    def end_execution(self) -> None:
        self.instance.running = False
        sys.exit(1)
