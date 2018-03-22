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
from pathlib import Path

import subcommands
import click
import toml
import colorama


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
@click.option("--config", "-c", default="config.toml",
              type=click.Path(exists=True),
              help="Specify alternate configuration file")
@click.pass_context
def main(ctx, verbose, config) -> None:
    """The Kamina service utility"""
    conf = load_config(config)
    colorama.init()  # Initialize colorama

    # There might not have been any configuration loaded, so let's at least set
    # a baseline - these two values should at least be known.
    if "verbose" not in conf:
        conf["verbose"] = verbose

    # Now override the config file defaults with any command line options
    if verbose:
        conf["verbose"] = True

    # Replace some variables in config, mainly ${HOME} and ${NODEDIR}
    conf = parse_config_variables(conf)

    # Now, propogate the context for our sub-commands
    ctx.obj["CONF"] = conf
    ctx.obj["BASIC_COMMANDS"] = subcommands.BasicCommands(ctx.obj["CONF"])
    ctx.obj["ADVANCED_COMMANDS"] = subcommands.AdvancedCommands(ctx.obj["CONF"])


@main.command()
@click.option("--install-ipfs", is_flag=True, help="Install ipfs locally for this platform.")
@click.pass_context
def init(ctx, install_ipfs) -> None:
    """Setup a new community node"""
    verbose = ctx.obj["CONF"]["verbose"]
    try:
        ctx.obj["BASIC_COMMANDS"].setup_community_node(install_ipfs)
    except Exception as error:
        if verbose:
            print(error)
        else:
            print("There was a problem setting up the node, use --verbose for more information.")


@main.command()
@click.pass_context
def daemon(ctx) -> None:
    """Initialize a community daemon"""
    ctx.obj["ADVANCED_COMMANDS"].start_community_daemon()


if __name__ == "__main__":
    main(obj={})
