import sys
import signal
import time

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
kamina.daemon.py - Process and Thread handlers for backgrounded Kamina instances

Provides a python class for maintaining some consistent state across processes 
and threads.  
"""


class KaminaInstance:
    """Class providing state for the Kamina daemon"""

    # Not providing any defaults here, as an instance needs at least some conf
    # and a logger to speak out to.
    def __init__(self, conf, logger) -> None:
        self.running = False

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

    def signal_handler(self, signum, frame):
        sys.stdout.write("\naborting on signal %s\n" % signum)
        sys.stdout.flush()

        self.running = False
        raise Exception

    def setup(self) -> None:
        """Called to initialize a new Kamina instance"""

        self.running = True

        # setup our signal handlers
        # I don't do this in __init__, because having the class initialized
        # doesn't mean we're invoking any methods.  At least not yet.
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        time.sleep(5)

        self.running = False
