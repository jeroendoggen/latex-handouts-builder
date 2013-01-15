""" Build Script for Latex-beamer based course handouts

Copyright (C) 2013  Jeroen Doggen <jeroendoggen@gmail.com>

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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA  02110-1301, USA.

"""

from __future__ import print_function, division  # We require Python 2.6+

import os
import sys
import datetime
import subprocess
import time
import signal

CONFIG_FILE = "chapters.conf"
SCRIPTPATH = os.getcwd()
FAILED_BUILDS = []


def read_chapters_file(config_file):
    """Read the config file to get the list of chapters"""
    try:
        with open(config_file, "r") as configfile:
            chapters_list = configfile.read().splitlines()
    except IOError:
        print ("Error: 'chapters.conf' not found!")
        print ("Aborting test session.")
        sys.exit(1)
    return chapters_list


def print_chapters(chapters_list):
    """Print an overview of all the chapters"""
    print("The following chapters will be processed:")
    for index, item in enumerate(chapters_list):
        print (" ", end="")
        print (index + 1, end="")
        print (". ", end="")
        print (item)
    print("")


def timed_cmd(command, timeout):
    """Call a cmd and kill it after 'timeout' seconds"""
    cmd = command.split(" ")
    print(command)
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)

    while process.poll() is None:
        now = datetime.datetime.now()
        time.sleep(1)
        if (now - start).seconds > timeout:
            print ("Process timeout")
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process.poll()


def build_chapters(chapters_list):
    """Print an overview of all the chapters"""
    for index, current_chapter in enumerate(chapters_list):
        try:
            os.chdir(SCRIPTPATH)
        except OSError:
            print("Error: unable to open the script folder")
            print("This should never happen...")
        try:
            os.chdir(current_chapter)
            found_test_path = True
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("mv" + " " + current_chapter + ".pdf"
              + " " + "../Handouts"), 10)
        except OSError:
            print("Error: unable to open test folder")
            print("Check your config file")
            found_test_path = False
            FAILED_BUILDS.append(current_chapter)


def run():
    """Run the main program"""
    chapters_list = read_chapters_file(CONFIG_FILE)
    print_chapters(chapters_list)
    build_chapters(chapters_list)
    return(0)


if __name__ == "__main__":
    sys.exit(run())
