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
logger.py - Class that simplifies logging/output to console
"""

import sys

from colorama import Style, Fore

from core.instance import KaminaInstance

class Logger:
    def __init__(self, instance: KaminaInstance):
        self.instance = instance

    def print_verbose(self, message: str) -> None:
        self.instance.logger.info(self.__verbose_msg() + message)

    def print_error(self, message: str) -> None:
        self.instance.logger.error(self.__error_msg() + message)
        self.end_execution()

    def print_info(self, message: str) -> None:
        self.instance.logger.info(self.__info_msg() + message)
        
    def end_execution(self):
        self.instance.running = False
        sys.exit(1)

    @staticmethod
    def __bright_msg(message: str) -> str:
        """Add bold escape character to message"""
        return Style.BRIGHT + message + Style.RESET_ALL

    def __error_msg(self) -> str:
        return self.__bright_msg(Fore.RED + "[ERROR] ")

    def __verbose_msg(self) -> str:
        return self.__bright_msg(Fore.BLUE + "[VERBOSE] ")

    def __info_msg(self) -> str:
        return self.__bright_msg(Fore.WHITE + "[INFO] ")
        