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
app.py - the command-line driver for Kamina.
This module parses command-line options, arguments, flags, and sub-commands.
It also instantiates a logger, deals with POSIX signals, loads JSON config
files, invokes the daemon process for a Kamina instance, and populates the
attributes of internal classes.
"""

import os
import sys
import json
import logging
import logging.config

import commands
import click


def load_config(filename="config.json") -> dict:
    """
    Open a JSON file, and parse their values into a dict
    :param filename: The config filename, defaults to $PWD/config.json
    :return: A dictionary containing the loaded configuration
    """
    config = {}

    if os.path.exists(filename):
        with open(filename, "rt") as cfg:
            try:
                config = json.load(cfg)
            except json.JSONDecodeError:
                print("Config file format is invalid! Providing defaults...")
    else:
        print("No config file found!")

    return config

# I have a low opinion of sigils, so function decorators have always looked
# like pythonic cancer.  Despite that, I've gotta admit the Click framework
# makes writing these cli apps insanely easy, so... I'll roll with it.


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=0.33, prog_name="kamina")
@click.option("--verbose", default=False, is_flag=True,
              help="Print all log messages to console")
@click.option("--debug", default=False, is_flag=True,
              help="Enable debugging")
@click.option("--log", "-l", default=None, type=click.Path(),
              help="Redirect logging location")
@click.option("--config", "-c", default="config.json",
              type=click.Path(exists=True),
              help="Specify alternate configuration file")
@click.pass_context
def main(ctx, verbose, debug, log, config) -> None:
    """The Kamina service utility"""

    logger = None
    handlers = []
    conf = {}

    conf = load_config(config)
    if "logging" in conf:
        logging.config.dictConfig(conf["logging"])

    # There might not have been any configuration loaded, so let's at least set
    # a baseline - these two values should at least be known.
    if "debug" not in conf:
        conf["debug"] = debug
    if "verbose" not in conf:
        conf["verbose"] = verbose

    # Now override the config file defaults with any command line options
    if debug:
        conf["debug"] = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # If you specified an alternate log location on the command-line, use that.
    # Otherwise, use syslog, so we at least have that, even if the config file
    # didn't specify any logging info.
    if log is not None:
        handlers.append(logging.FileHandler(log))
    else:
        # Make sure we're not setting up two syslog handlers
        if not logger.handlers:
            handlers.append(logging.handlers.SysLogHandler(address="/dev/log"))

    if verbose:
        conf["verbose"] = True
        handlers.append(logging.StreamHandler(sys.stdout))

    for handle in handlers:
        logger.addHandler(handle)

    # Now, propogate the context for our sub-commands
    ctx.obj["CONF"] = conf
    ctx.obj["LOG"] = logger
    ctx.obj["BASIC_COMMANDS"] = commands.BasicCommands(ctx)
    ctx.obj["ADVANCED_COMMANDS"] = commands.AdvancedCommands()


@main.command()
@click.option("--download-ipfs", is_flag=True, help="Download ipfs using this script.")
@click.pass_context
def init(ctx, download_ipfs) -> None:
    """Setup a new kamina-community node"""
    verbose = ctx.obj['CONF']['verbose']
    try:
        ctx.obj["BASIC_COMMANDS"].setup_community_node(download_ipfs)
    except Exception as error:
        if verbose:
            print(error)
        else:
            print("There was a problem setting up the node, use --verbose for more information.")


@main.command()
@click.pass_context
def daemon(ctx) -> None:
    """Initialize the kamina-community daemon"""
    ctx.obj["ADVANCED_COMMANDS"].start_community_daemon()


if __name__ == "__main__":
    main(obj={})
