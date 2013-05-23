""" Build Script for Latex-beamer based course handouts

Use multiple processes where possible to increase build speed

"""

from __future__ import print_function, division  # We require Python 2.6+

import os
import sys
import datetime
import subprocess
import time
import signal
import glob
import zipfile
import zlib
from multiprocessing import Process

"""User configurable settings:
CONFIG_FILE = the file with the list of chapters
HANDOUTSPATH = where do we want to place pdf document (and the final archive)
BOOK_TITLE = title of the handouts book tex file (without .tex !)
ARCHIVE_TITLE = name of the final archive (with .zip !)
BUILD_TIMEOUT = maximum time for a pdflatex build (default: 30s)

"""
CONFIG_FILE = "chapters.conf"
HANDOUTSPATH = "Handouts"
BOOK_TITLE = "ExampleHandoutsBook"
ARCHIVE_TITLE = "ExampleHandoutsBook.zip"
BUILD_TIMEOUT = 30

"""Global variables
TODO: make them local
"""
FAILED_BUILDS = []
SCRIPTPATH = os.getcwd()
FAILED_BUILDS = []
COUNTER = 0
TOTAL_TASKS = 0
TASKS_PER_CHAPTER = 5
START_TIME = 0
STOP_TIME = 0


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


def timed_cmd(command, timeout, path):
    """Call a cmd and kill it after 'timeout' seconds"""
    cmd = command.split(" ")
    #print_progress_counter(command)
    #print (path)
    #print (command)
    os.chdir(path)
    #print(os.getcwd())
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)

    while process.poll() is None:
        now = datetime.datetime.now()
        time.sleep(1)
        if (now - start).seconds > timeout:
            print (command)
            print ("Process timeout")
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process.poll()


def print_progress_counter(command):
    """Print the progress counter (e.g. 1/5, 2/5, ...)"""
    global COUNTER
    global TOTAL_TASKS
    COUNTER = COUNTER + 1
    print (COUNTER, end="/")
    print (TOTAL_TASKS, end=" ")


def builder_task(current_chapter):
    """Function to build a chapter, started as a process """
    try:
        timed_cmd(("pdflatex --output-directory=../" + HANDOUTSPATH + " " + current_chapter
          + ".tex"), BUILD_TIMEOUT, SCRIPTPATH + "/" + current_chapter)
        timed_cmd(("pdflatex --output-directory=../" + HANDOUTSPATH + " " + current_chapter
          + ".tex"), BUILD_TIMEOUT, SCRIPTPATH + "/" + current_chapter)
        timed_cmd(("pdflatex --output-directory=../" + HANDOUTSPATH + " " + current_chapter
          + "_pres.tex"), BUILD_TIMEOUT, SCRIPTPATH + "/" + current_chapter)
        timed_cmd(("pdflatex --output-directory=../" + HANDOUTSPATH + " " + current_chapter
          + "_pres.tex"), BUILD_TIMEOUT, SCRIPTPATH + "/" + current_chapter)
        timed_cmd(("pdfjam-slides6up " + current_chapter + ".pdf "
          + "--nup 2x3 --suffix 6pp -q"), BUILD_TIMEOUT, SCRIPTPATH + "/" + HANDOUTSPATH)
    except OSError:
        print("Error: unable to open test folder")
        print("Check your config file")
        FAILED_BUILDS.append(current_chapter)
    try:
        os.chdir(SCRIPTPATH)
    except OSError:
        print("Error: unable to open the script folder")
        print("This should never happen...")


def build_chapters(chapters_list):
    """Build all the chapters and move to handouts folder"""
    for index, current_chapter in enumerate(chapters_list):
        index = Process(target=builder_task, args=(current_chapter,))
        index.start()
    #Wait for all processes to finish (or just the one that is started last??)
    while (index.is_alive()):
        time.sleep(1)


def build_book(book_title):
    """Build the handouts book"""
    try:
        os.chdir(SCRIPTPATH)
        os.chdir(HANDOUTSPATH)
        timed_cmd(("pdflatex" + " " + book_title), BUILD_TIMEOUT, SCRIPTPATH + "/" + HANDOUTSPATH)
        timed_cmd(("pdflatex" + " " + book_title), BUILD_TIMEOUT, SCRIPTPATH + "/" + HANDOUTSPATH)
    except OSError:
        print("Error: unable build the final book")
        FAILED_BUILDS.append("The book:" + book_title)


def cleanup():
    """Clean temporary files
    List taken from Kile
    .aux .bit .blg .bbl .lof .log .lot .glo .glx .gxg .gxs .idx .ilg .ind
    .out .url .svn .toc
     My extra's
    *~ .snm .nav
    """
    types = ('*.aux', '*.bit', '*.blg', '*.bbl', '*.lof', '*.log', '*.glo',
             '*.glx', '*.gxg', '*.gxs', '*.idx', '*.ilg', '*.ind', '*.out',
             '*.url', '*.svn', '*.toc',  '*~', '*.snm', '*.nav')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(files))
    for filename in files_grabbed:
        #print(filename)
        os.remove(filename)

def cleanup_chapters(chapters_list):
    """Cleanup all the chapters"""
    for index, current_chapter in enumerate(chapters_list):
        try:
            os.chdir(SCRIPTPATH + "/" + current_chapter)
            cleanup()
        except OSError:
            print("Error: unable to open chapter folder: " + current_chapter)
    try:
        os.chdir(SCRIPTPATH + "/" + HANDOUTSPATH)
        cleanup()
    except OSError:
        print("Error: unable to open the handouts folder during cleanup")
        print("This should never happen...")


def create_archive(chapters_list):
    """Build the archive with all slides and the book"""
    try:
        os.chdir(SCRIPTPATH)
        os.chdir(HANDOUTSPATH)
        compression = zipfile.ZIP_DEFLATED
        archive = zipfile.ZipFile(ARCHIVE_TITLE, mode='w')
        try:
            for index, current_chapter in enumerate(chapters_list):
                archive.write(current_chapter + ".pdf",
                  compress_type=compression)
                #os.remove(current_chapter + ".pdf")
                #os.remove(current_chapter + "-6pp.pdf")
            archive.write(BOOK_TITLE + ".pdf", compress_type=compression)
            #os.remove(BOOK_TITLE + ".pdf")
        finally:
            archive.close()
    except OSError:
        print("Error: unable build the archive: " + ARCHIVE_TITLE)
        FAILED_BUILDS.append("Failed to build archive:" + ARCHIVE_TITLE)


def print_summary(passedtime):
    """Print a summary of the build process"""
    print("Output written to: " + ARCHIVE_TITLE)
    print("Build took " + str(passedtime) + " seconds")


def timing(action):
    """Calculate the runtime of the program in seconds"""
    if action == "start":
        global START_TIME
        START_TIME = datetime.datetime.now()
    if action == "stop":
        global STOP_TIME
        STOP_TIME = datetime.datetime.now()
        passedtime = STOP_TIME - START_TIME
        return (passedtime.seconds)


def run():
    """Run the main program"""
    global TOTAL_TASKS
    timing("start")
    chapters_list = read_chapters_file(CONFIG_FILE)
    TOTAL_TASKS = TASKS_PER_CHAPTER * count_chapters(chapters_list) + 2 + 1
    print_chapters(chapters_list, BOOK_TITLE)
    build_chapters(chapters_list,)
    build_book(BOOK_TITLE)
    create_archive(chapters_list)
    print_summary(timing("stop"))
    #time.sleep(1)
    cleanup_chapters(chapters_list)
    return(0)


if __name__ == "__main__":
    sys.exit(run())
