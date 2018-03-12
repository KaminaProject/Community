import itertools
import os
import sys
import json
import threading
import logging
import logging.config
import click
import Kamina

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

"""
app.py - the command-line driver for Kamina.

This module parses command-line options, arguments, flags, and sub-commands.  
It also instantiates a logger, loads JSON configuration files, invokes the 
daemon process for a Kamina instance, and populates the attributes of the 
internal daemon class.  
"""

#
# load_config - open a JSON file, and parse their values into a dict
#


def load_config(filename="config.json") -> dict:
    config = {}

    if os.path.exists(filename):
        with open(filename, "rt") as cfg:
            try:
                config = json.load(cfg)
            except:
                print("Config file format is invalid! Providing defaults...")
    else:
        print("No config file found!")

    return config

# I have a low opinion of sigils, so function decorators have always looked
# like pythonic cancer.  Despite that, I've gotta admit the Click framework
# makes writing these cli apps insanely easy, so... I'll roll with it.


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=0.33, prog_name="Kamina")
@click.option("--verbose", default=False, is_flag=True, help="Print all log messages to console")
@click.option("--debug", default=False, is_flag=True, help="Enable debugging")
@click.option("--log", "-l", default=None, type=click.Path(), help="Redirect logging location")
@click.option("--config", "-c", default="config.json", type=click.Path(exists=True),
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
        if not len(logger.handlers):
            handlers.append(logging.handlers.SysLogHandler(address="/dev/log"))

    if verbose:
        conf["verbose"] = True
        handlers.append(logging.StreamHandler(sys.stdout))

    for handle in handlers:
        logger.addHandler(handle)

    # Now, propogate the context for our sub-commands
    ctx.obj["CONF"] = conf
    ctx.obj["LOG"] = logger


@main.command()
@click.option("--download-ipfs", is_flag=True, help="Download ipfs using this script.")
@click.pass_context
def init(ctx, download_ipfs) -> None:
    """Setup a new Kamina instance"""

    logger = None
    spinner = ""
    conf = {}

    # Grab our context from main for logging and config info.
    logger = ctx.obj["LOG"]
    conf = ctx.obj["CONF"]
    spinner = itertools.cycle(['-', '/', '|', '\\'])

    if logger is None or len(conf) == 0:
        print("init:  no valid conf or logger passed.  Exiting.")
        sys.exit(1)

    logger.info("Setting up a new Kamina instance...")
    try:
        daemon = Kamina.KaminaInstance(conf, logger)
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        setup_thread = threading.Thread(target=daemon.setup, args=(download_ipfs,))
        setup_thread.start()
        # If we're running in production, give a nice fidget spinner
        if not conf["verbose"]:
            print("Setting up a new Kamina instance....")
            while daemon.running:
                sys.stdout.write(next(spinner))
                sys.stdout.write('\b')
                sys.stdout.flush()
    except Exception as e:
        sys.stdout.write("\bfailed!")
        sys.stdout.flush()

        print(e)
        sys.exit(1)
    else:
        sys.stdout.write("\bdone!")
        sys.stdout.flush()
        sys.exit(0)


@main.command()
def daemon() -> None:
    """Run the Kamina service as a daemon"""

    pass


@main.command(short_help="Manually create a post", help="Manually create a post identified by <postid>")
@click.argument("postid", metavar="<postid>")
def create(postid) -> None:
    pass


@main.command(short_help="Manually delete a post", help="Manually delete a post identified by <postid>")
@click.argument("postid", metavar="<postid>")
def delete(postid) -> None:
    click.echo("Delete called")


@main.command()
def archive() -> None:
    """Set all posts to expire"""

    pass


@main.command(short_help="Reload system modules")
@click.argument("module", default=None, required=False, nargs=1)
def reload(module) -> None:
    """Valid modules are [posts|media|net] or blank to reload all"""

    pass


@main.command()
@click.argument('topic', default=None, required=False, nargs=1)
@click.pass_context
def help(ctx, topic) -> None:
    """Print this help message and exit"""

    if topic is None:
        click.echo(ctx.parent.get_help())
    else:
        click.echo(main.commands[topic].get_help(ctx))


if __name__ == "__main__":
    main(obj={})
