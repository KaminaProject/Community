#!/usr/bin/env python3
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
settings.py - Load and parse configuration files
"""

import sys
import os
import logging
import logging.config
import logging.handlers
from pathlib import Path, PurePath

import yaml


class KaminaConfiguration:
    """
    Helper class to load and parse config files in conf folder
    """
    def __init__(self, base_dir: str):
        # TODO: Set needed defaults
        self.conf = {}
        self.base_dir = base_dir
        self.conf_dir = PurePath(base_dir, "conf")
        self.logger = logging.getLogger()
        if not os.path.exists(self.conf_dir):
            print(self.conf_dir)
            print("Config dir not found")
            sys.exit(1)
        self._setup_logger()
        self._load_conf()
        self.conf = self._replace_vars(self.conf)  # Damn recursion lol

    def _setup_logger(self):
        # Try to open logging config
        with open(PurePath(self.conf_dir, "logging.yaml"), "rt") as log_cfg:
            try:
                logging_conf = yaml.load(log_cfg)
            except yaml.YAMLError:
                print("Error parsing logging configuration.")
                sys.exit(1)

        # Setup logging
        try:
            logging.config.dictConfig(logging_conf)
        except (ImportError, ValueError, TypeError, AttributeError):
            print("Error configurating logger, using defaults")
            self._setup_logger_defaults()
        else:
            self.logger = logging.getLogger("kamina")

    def _setup_logger_defaults(self):
        self.logger = logging.getLogger("kamina")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.addHandler(logging.FileHandler(PurePath(self.base_dir, "kamina.log")))

    def _load_conf(self):
        with open(PurePath(self.conf_dir, "kamina.yaml"), "rt") as cfg:
            try:
                self.conf = yaml.load(cfg)
            except yaml.YAMLError:
                self.logger.error("Error parsing kamina.yaml")
                sys.exit(1)

    def _replace_vars(self, config: dict):
        """
            Replace some variables in the config dict:
            It only replaces ${HOME} for now
            """
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_vars(value)
            else:
                if isinstance(value, str):
                    if value.find("${HOME}") != -1:
                        config[key] = value.replace("${HOME}", str(Path.home()))
        return config
