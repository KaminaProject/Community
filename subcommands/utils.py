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
utils.py - Handy utility methods
"""

from pprint import pprint
from inspect import getmembers
from colorama import Style, Fore


def var_dump(var: object) -> None:
    """ Mimmic PHP's var_dump"""
    pprint(getmembers(var))


def bright_msg(message: str) -> str:
    """Add escape characters to message for bold printing"""
    return Style.BRIGHT + message + Style.RESET_ALL


def error_msg() -> str:
    return bright_msg(Fore.RED + "[ERROR] ")


def verbose_msg() -> str:
    return bright_msg(Fore.BLUE + "[VERBOSE] ")


def info_msg() -> str:
    return bright_msg(Fore.WHITE + "[INFO] ")
