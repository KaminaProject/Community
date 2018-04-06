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
import logging
import logging.config
import logging.handlers
import threading
import signal
import importlib
from pathlib import Path

import click
import toml
import colorama

from core.instance import KaminaInstance

# Some global variables
KAMINA_INSTANCE = None
CLI_COMMANDS = None


def load_config(filename="config.toml") -> dict:
    """
    Open a TOML file, and parse their values into a dict
    """
    config = {}

    if os.path.exists(filename):
        with open(filename, "rt") as cfg:
            try:
                config = toml.load(cfg)
            except toml.TomlDecodeError:
                print("Config file format is invalid! Providing defaults...")
    else:
        print("No config file found!")

    return config


def parse_config_variables(config: dict) -> dict:
    for key, value in config.items():
        if isinstance(value, dict):
            parse_config_variables(value)
        else:
            if isinstance(value, str):
                if value.find("${HOME}") != -1:
                    config[key] = value.replace("${HOME}", str(Path.home()))
    return config

# I have a low opinion of sigils, so function decorators have always looked
# like pythonic cancer.  Despite that, I've gotta admit the Click framework
# makes writing these cli apps insanely easy, so... I'll roll with it.


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=0.1, prog_name="Kamina Community")
@click.option("--verbose", default=False,
              is_flag=True,
              help="Print all log messages to console, must be before any subcommand")
@click.option("--debug", default=False, is_flag=True,
              help="Enable debugging")
@click.option("--log", "-l", default=None, type=click.Path(),
              help="Redirect logging location")
@click.option("--config", "-c", default="config.toml",
              type=click.Path(exists=True),
              help="Specify alternate configuration file")
@click.pass_context
def main(ctx, verbose, debug, log, config) -> None:
    global CLI_COMMANDS
    global KAMINA_INSTANCE
    """The Kamina service utility"""
    conf = load_config(config)
    colorama.init()  # Initialize colorama
    handlers = []

    if "logging" in conf:
        logging.config.dictConfig(conf["logging"])

    handlers.append(logging.StreamHandler(sys.stdout))

    # There might not have been any configuration loaded, so let's at least set
    # a baseline - these two values should at least be known.
    if "debug" not in conf:
        conf["debug"] = debug
    if "verbose" not in conf:
        conf["verbose"] = verbose
    if "enable_ipfs" not in conf:
        conf["enable_ipfs"] = True

    # Now override the config file defaults with any command line options
    if debug:
        conf["debug"] = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Replace some variables in config, mainly ${HOME} and ${NODEDIR}
    conf = parse_config_variables(conf)

    # If you specified an alternate log location on the command-line, use that.
    # Otherwise, use syslog, so we at least have that, even if the config file
    # didn't specify any logging info.
    if log:
        handlers.append(logging.FileHandler(log))
    else:
        # Make sure we're not setting up two syslog handlers
        if not logger.handlers:
            handlers.append(logging.handlers.SysLogHandler(address="/dev/log"))

    if verbose:
        conf["verbose"] = True

    for handle in handlers:
        logger.addHandler(handle)

    # Now, propogate the context for our sub-commands
    ctx.obj["CONF"] = conf
    ctx.obj["LOG"] = logger

    # Give value to our globals
    KAMINA_INSTANCE = KaminaInstance(conf, logger)
    if not conf["enable_ipfs"]:
        CLI_COMMANDS = importlib.import_module("core.non-ipfs.cli_commands").CliCommands(conf)
    else:
        CLI_COMMANDS = importlib.import_module("core.ipfs.cli_commands").CliCommands(conf)

    # Register instance
    try:
        CLI_COMMANDS.register_instance(KAMINA_INSTANCE)
    except Exception as error:
        print(error)
        sys.exit(1)


@main.command()
@click.option("--install-ipfs", is_flag=True, help="Install ipfs locally.")
@click.pass_context
def init(ctx, install_ipfs) -> None:
    """Setup a new community node"""
    logger = ctx.obj["LOG"]
    conf = ctx.obj["CONF"]
    signal_thunk = signal.signal(signal.SIGINT, signal.SIG_IGN)
    cli_commands = CLI_COMMANDS
    instance = KAMINA_INSTANCE

    if not logger or not conf:
        print("Error: no valid conf or logger passed. Exiting.")
        sys.exit(1)

    try:
        setup_thread = threading.Thread(
            target=cli_commands.init,
            args=(install_ipfs,))
        signal.signal(signal.SIGINT, signal_thunk)
        setup_thread.start()
    except KeyboardInterrupt:
        instance.running = False
        sys.stdout.write("\bAborted!\n")
        sys.stdout.flush()
    except Exception as error:
        sys.stdout.write("\bFailed!")
        sys.stdout.write("\n%s" % error)
        sys.stdout.flush()
    else:  # No exception ocurred
        setup_thread.join()
        sys.stdout.flush()

    sys.exit(0)


@main.command()
@click.pass_context
def daemon(ctx) -> None:
    """Initialize a community daemon"""
    cli_commands = CLI_COMMANDS
    cli_commands.daemon()


if __name__ == "__main__":
    main(obj={})
