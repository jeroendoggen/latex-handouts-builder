""" Build Script for Latex-beamer based course handouts

Using one process: helpful for debugging LaTeX build errors.

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

"""User configurable settings:
CONFIG_FILE = the file with the list of chapters
HANDOUTSPATH = where do we want to place pdf document (and the final archive)
BOOK_TITLE = title of the handouts book tex file (without .tex)
ARCHIVE_TITLE = name of the final archive

"""
CONFIG_FILE = "chapters.conf"
HANDOUTSPATH = "Handouts"
BOOK_TITLE = "ExampleHandoutsBook"
BOOK_TITLE_NOTES = "ExampleHandoutsBookNotes"
BOOK_TITLE_2PP = "ExampleHandoutsBookTwo"
ARCHIVE_TITLE = "ExampleHandoutsBook.zip"
NOTES = "_4pp-Notes"
TWO_PER_PAGE = "_2pp"
PRESENTATION = "_pres"

"""Global variables
TODO: make them local, using classes
"""
FAILED_BUILDS = []
FAILED_BUILD_COUNTER = 0
SCRIPTPATH = os.getcwd()
FAILED_BUILDS = []
COUNTER = 0
TOTAL_TASKS = 0
TASKS_PER_CHAPTER = 14
START_TIME = 0
STOP_TIME = 0

"""Enabling features
Used to handle course handouts for classes with incomplete slide sets
"""

BUILD_HANDOUTS = True
#BUILD_HANDOUTS = False

BUILD_HANDOUTS_2PP = True
#BUILD_HANDOUTS_2PP = False

BUILD_HANDOUTS_NOTES = True
#BUILD_HANDOUTS_NOTES = False

BUILD_PRESENTATION_SLIDES = True
#BUILD_PRESENTATION_SLIDES = False

CLEANUP = True
#CLEANUP = False


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
    global FAILED_BUILD_COUNTER
    cmd = command.split(" ")
    print_progress_counter()
    print (command)
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    while process.poll() is None:
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            print ("Process timeout")
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            FAILED_BUILD_COUNTER = FAILED_BUILD_COUNTER + 1
            return None
        time.sleep(0.01)
    return process.poll()


def print_progress_counter():
    """Print the progress counter (e.g. 1/5, 2/5, ...)"""
    global COUNTER
    global TOTAL_TASKS
    COUNTER = COUNTER + 1
    print (COUNTER, end="/")
    print (TOTAL_TASKS, end=" ")


def build_chapters(chapters_list):
    """Build all the chapters and move to handouts folder"""
    global FAILED_BUILD_COUNTER
    for current_chapter in chapters_list:
        try:
            os.chdir(current_chapter)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdfjam-slides6up" + " " + current_chapter + ".pdf "
                       + "--nup 2x3 --suffix 6pp -q "), 10)
            timed_cmd(("mv" + " " + current_chapter + ".pdf"
                       + " " + "../" + HANDOUTSPATH), 10)
            timed_cmd(("mv" + " " + current_chapter + "-6pp" + ".pdf"
                       + " " + "../" + HANDOUTSPATH), 10)
            cleanup()
        except OSError:
            print("Error: unable to open test folder")
            print("Check your config file")
            FAILED_BUILDS.append(current_chapter)
            FAILED_BUILD_COUNTER = FAILED_BUILD_COUNTER + 1
        try:
            os.chdir(SCRIPTPATH)
        except OSError:
            print("Error: unable to open the script folder")
            print("This should never happen...")
            FAILED_BUILD_COUNTER = FAILED_BUILD_COUNTER + 1


def build_chapters_notes(chapters_list):
    """Build all the chapters and move to handouts folder"""
    for index, current_chapter in enumerate(chapters_list):
        try:
            os.chdir(current_chapter)
            current_chapter = current_chapter + NOTES
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("mv" + " " + current_chapter + ".pdf"
                       + " " + "../" + HANDOUTSPATH), 10)
            cleanup()
        except OSError:
            print("Error: unable to open test folder")
            print("Check your config file")
            FAILED_BUILDS.append(current_chapter)
        try:
            os.chdir(SCRIPTPATH)
        except OSError:
            print("Error: unable to open the script folder")
            print("This should never happen...")


def build_chapters_2pp(chapters_list):
    """Build all the chapters and move to handouts folder"""
    for index, current_chapter in enumerate(chapters_list):
        try:
            os.chdir(current_chapter)
            current_chapter = current_chapter + TWO_PER_PAGE
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("mv" + " " + current_chapter + ".pdf"
                       + " " + "../" + HANDOUTSPATH), 10)
            cleanup()
        except OSError:
            print("Error: unable to open test folder")
            print("Check your config file")
            FAILED_BUILDS.append(current_chapter)
        try:
            os.chdir(SCRIPTPATH)
        except OSError:
            print("Error: unable to open the script folder")
            print("This should never happen...")


def build_chapters_presentation(chapters_list):
    """Build all the chapters and move to handouts folder"""
    for index, current_chapter in enumerate(chapters_list):
        try:
            os.chdir(current_chapter)
            current_chapter = current_chapter + PRESENTATION
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("pdflatex" + " " + current_chapter), 10)
            timed_cmd(("mv" + " " + current_chapter + ".pdf"
                       + " " + "../" + HANDOUTSPATH), 10)
            cleanup()
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
        os.chdir(HANDOUTSPATH)
        timed_cmd(("pdflatex" + " " + book_title), 10)
        timed_cmd(("pdflatex" + " " + book_title), 10)
        cleanup()
        os.chdir(SCRIPTPATH)
    except OSError:
        print("Error: unable build the final book")
        FAILED_BUILDS.append("The book:" + book_title)


def cleanup():
    """Clean temporary files
    List taken from Kile:
    .aux .bit .blg .bbl .lof .log .lot .glo .glx .gxg .gxs .idx .ilg .ind
    .out .url .svn .toc
     My extra's:
    *~ .snm .nav
    """
    types = ('*.aux', '*.bit', '*.blg', '*.bbl', '*.lof', '*.log', '*.glo',
             '*.glx', '*.gxg', '*.gxs', '*.idx', '*.ilg', '*.ind', '*.out',
             '*.url', '*.svn', '*.toc',  '*~', '*.snm', '*.nav')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(files))
    for filename in files_grabbed:
        os.remove(filename)


def create_archive(chapters_list):
    """Build the archive with all slides and the book"""
    try:
        os.chdir(SCRIPTPATH)
        os.chdir(HANDOUTSPATH)
        compression = zipfile.ZIP_DEFLATED
        archive = zipfile.ZipFile(ARCHIVE_TITLE, mode='w')
        try:
            for current_chapter in chapters_list:
                archive.write(current_chapter + ".pdf",
                    compress_type=compression)
                if(BUILD_PRESENTATION_SLIDES):
                    archive.write(current_chapter + PRESENTATION + ".pdf",
                        compress_type=compression)
                if(CLEANUP):
                    clean_chapter_pdf_files(current_chapter)
            if(BUILD_HANDOUTS):
                archive.write(BOOK_TITLE + ".pdf",
                    compress_type=compression)
            if(BUILD_HANDOUTS_NOTES):
                archive.write(BOOK_TITLE_NOTES + ".pdf",
                    compress_type=compression)
            if(BUILD_HANDOUTS_2PP):
                archive.write(BOOK_TITLE_2PP + ".pdf",
                    compress_type=compression)
            if(CLEANUP):
                clean_book_pdf_files()
        finally:
            archive.close()
    except OSError:
        print("Error: unable build the archive: " + ARCHIVE_TITLE)
        FAILED_BUILDS.append("Failed to build archive:" + ARCHIVE_TITLE)


def clean_chapter_pdf_files(current_chapter):
    """Remove temporary pdf files in handouts folder (chapter slides)"""
    os.remove(current_chapter + ".pdf")
    os.remove(current_chapter + NOTES + ".pdf")
    os.remove(current_chapter + "_2pp.pdf")
    os.remove(current_chapter + "-6pp.pdf")
    os.remove(current_chapter + PRESENTATION + ".pdf")


def clean_book_pdf_files():
    """Remove temporary pdf files in handouts folder (books)"""
    os.remove(BOOK_TITLE + ".pdf")
    os.remove(BOOK_TITLE_NOTES + ".pdf")
    os.remove(BOOK_TITLE_2PP + ".pdf")


def print_summary(passedtime):
    """Print a summary of the build process"""
    print("Number of errors: ", end="")
    print(FAILED_BUILD_COUNTER)
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


def calculate_total_tasks(chapters_list):
    """get correct counter values based on enabled build options"""
    global TOTAL_TASKS

    chaptercount = count_chapters(chapters_list)
    if (BUILD_HANDOUTS):
        TOTAL_TASKS = TOTAL_TASKS + 5 * chaptercount + 2
    if (BUILD_HANDOUTS_2PP):
        TOTAL_TASKS = TOTAL_TASKS + 3 * chaptercount + 2
    if (BUILD_HANDOUTS_NOTES):
        TOTAL_TASKS = TOTAL_TASKS + 3 * chaptercount + 2
    if (BUILD_PRESENTATION_SLIDES):
        TOTAL_TASKS = TOTAL_TASKS + 3 * chaptercount


def run():
    """Run the main program"""
    global TOTAL_TASKS
    timing("start")
    chapters_list = read_chapters_file(CONFIG_FILE)
    calculate_total_tasks(chapters_list)
    print_chapters(chapters_list, BOOK_TITLE)
    if(BUILD_HANDOUTS):
        build_chapters(chapters_list,)
        build_book(BOOK_TITLE)
    if(BUILD_HANDOUTS_NOTES):
        build_chapters_notes(chapters_list,)
        build_book(BOOK_TITLE_NOTES)
    if(BUILD_HANDOUTS_2PP):
        build_chapters_2pp(chapters_list,)
        build_book(BOOK_TITLE_2PP)
    if(BUILD_PRESENTATION_SLIDES):
        build_chapters_presentation(chapters_list,)
    create_archive(chapters_list)
    print_summary(timing("stop"))
    return(0)


if __name__ == "__main__":
    sys.exit(run())
