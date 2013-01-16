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
BOOK_TITLE = "ExampleHandoutsBook"
COUNTER = 0
TOTAL_TASKS = 0


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


def count_chapters(chapters_list):
    """Count the number of chapters in the chapters list"""
    counter = 0
    for index in enumerate(chapters_list):
        counter = counter + 1
    return (counter)


def print_chapters(chapters_list, book_title):
    """Print an overview of all the chapters"""
    print("The following files will be processed:")
    index = 0
    for index, item in enumerate(chapters_list):
        print (" ", end="")
        print (index + 1, end="")
        print (". ", end="")
        print (item, end=".tex")
        print ("")
    print (" ", end="")
    print (index + 2, end="")
    print (". ", end="")
    print (book_title, end=".tex")
    print ("")
    print ("")


def timed_cmd(command, timeout):
    """Call a cmd and kill it after 'timeout' seconds"""
    cmd = command.split(" ")
    print_progress_counter(command)
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


def print_progress_counter(command):
    """Build the progress counter (e.g. 1/5, 2/5, ...)"""
    global COUNTER
    global TOTAL_TASKS
    COUNTER = COUNTER + 1
    print (COUNTER, end="/")
    print (TOTAL_TASKS, end=" ")
    print (command)


def build_chapters(chapters_list):
    """Build all the chapters and move to handouts folder"""
    for index, current_chapter in enumerate(chapters_list):
        try:
            os.chdir(current_chapter)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdfjam-slides6up" + " " + current_chapter + ".pdf "
              + "--nup 2x3 --suffix 6pp -q"), 10)
            timed_cmd(("mv" + " " + current_chapter + ".pdf"
              + " " + "../Handouts"), 10)
            timed_cmd(("mv" + " " + current_chapter + "-6pp" + ".pdf"
              + " " + "../Handouts"), 10)
        except OSError:
            print("Error: unable to open test folder")
            print("Check your config file")
            FAILED_BUILDS.append(current_chapter)
        try:
            os.chdir(SCRIPTPATH)
        except OSError:
            print("Error: unable to open the script folder")
            print("This should never happen...")


def build_book(book_title):
    """Build the handouts book"""
    try:
        os.chdir("Handouts")
        timed_cmd(("pdflatex" + " " + book_title), 10)
        timed_cmd(("pdflatex" + " " + book_title), 10)
        print ("Build finished")
        print ("Output written to: ", end="")
        print (book_title, end=".pdf")
        print ("")
    except OSError:
        print("Error: unable build the final book")
        FAILED_BUILDS.append("The book:" + book_title)


def run():
    """Run the main program"""
    global TOTAL_TASKS
    chapters_list = read_chapters_file(CONFIG_FILE)
    TOTAL_TASKS = 5 * count_chapters(chapters_list) + 2
    print_chapters(chapters_list, BOOK_TITLE)
    build_chapters(chapters_list,)
    build_book(BOOK_TITLE)
    return(0)


if __name__ == "__main__":
    sys.exit(run())
