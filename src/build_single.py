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


class Settings:
    """ Contains all the tools to analyse Blackboard assignments """
    logfile = "blackboard_analysis_tools.log"
    config_file = "chapters.conf"
    handouts_path = "Handouts"
    book_title = "ExampleHandoutsBook"
    book_title_notes = "ExampleHandoutsBookNotes"
    book_title_2pp = "ExampleHandoutsBookTwo"
    archive_title = "ExampleHandoutsBook.zip"
    notes_suffix = "_4pp-Notes"
    two_per_page_suffix = "_2pp"
    presentation_suffix = "_pres"
    script_path = os.getcwd()

    build_handouts = True
    #build_handouts = False

    build_handouts_2pp = True
    #build_handouts_2pp = False

    build_handouts_notes = True
    #build_handouts_notes = False

    build_presentation_slides = True
    #build_presentation_slides = False

    cleanup = True
    #cleanup = False

    def __init__(self):
        pass


class HandoutsBuilder:
    """ Contains all the tools to build the LaTeX beamer based handouts """
    chapters_list = ""
    chapter_counter = 0
    failed_builds_counter = 0
    failed_builds_list = []
    total_tasks_counter = 0
    current_task_counter = 0

    def __init__(self):
        """ Initialisations"""
        self.settings = Settings()
        #self.reporter = Reporter(self.settings)

    def run(self):
        """ Run the actual program (call this from main) """
        self.timing("start")
        self.get_chapters_list(self.settings.config_file)
        self.count_total_chapters()
        self.calculate_total_tasks()
        self.print_chapters(self.settings.book_title)
        self.build_handouts()
        self.create_archive()
        #self.print_summary(timing("stop"))
        return(0)

    def exit_value(self):
        #"""TODO: Generate the exit value for the application."""
        #if (self.errors == 0):
        if (True):
            return 0
        else:
            return 42

    def timing(self, action):
        """Calculate the runtime of the program in seconds """
        if action == "start":
            self.start_time = datetime.datetime.now()
        if action == "stop":
            self.stop_time = datetime.datetime.now()
            passedtime = self.stop_time - self.start_time
            return (passedtime.seconds)

    def get_chapters_list(self, config_file):
        """ Read the config file to get the list of chapters """
        try:
            with open(config_file, "r") as configfile:
                self.chapters_list = configfile.read().splitlines()
        except IOError:
            print ("Error: 'chapters.conf' not found!")
            print ("Aborting test session.")
            sys.exit(1)

    def count_total_chapters(self):
        """ Count the number of chapters in the chapters list """
        for index in enumerate(self.chapters_list):
            self.chapter_counter = self.chapter_counter + 1

    def print_chapters(self, book_title):
        """ Print an overview of all the chapters """
        print("The following files will be processed:")
        index = 0
        for index, item in enumerate(self.chapters_list):
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

    def build_handouts(self):
        """ Build the actual handouts """
        if(self.settings.build_handouts):
            self.build_chapters(self.chapters_list, "default")
            self.build_book(self.settings.book_title)
        if(self.settings.build_handouts_notes):
            self.build_chapters(self.chapters_list, self.settings.notes_suffix)
            self.build_book(self.settings.book_title_notes)
        if(self.settings.build_handouts_2pp):
            self.build_chapters(self.chapters_list,
                self.settings.two_per_page_suffix)
            self.build_book(self.settings.book_title_2pp)
        self.build_chapters(self.chapters_list,
            self.settings.presentation_suffix)

    def build_chapters(self, chapters_list, chapter_type):
        """ Build all the chapters and move to handouts folder """
        if chapter_type == "default":
            suffix = ""
        if chapter_type == self.settings.notes_suffix:
            suffix = self.settings.notes_suffix
        if chapter_type == self.settings.two_per_page_suffix:
            suffix = self.settings.two_per_page_suffix
        if chapter_type == self.settings.presentation_suffix:
            suffix = self.settings.presentation_suffix

        for current_chapter in chapters_list:
            try:
                os.chdir(current_chapter)
                current_chapter = current_chapter + suffix
                self.timed_cmd(("pdflatex" + " " + current_chapter), 10)
                self.timed_cmd(("pdflatex" + " " + current_chapter), 10)
                if chapter_type == "default":
                    self.timed_cmd(("pdfjam-slides6up"
                            + " " + current_chapter + ".pdf "
                            + "--nup 2x3 --suffix 6pp -q "), 10)
                self.timed_cmd(("mv" + " " + current_chapter + ".pdf"
                        + " " + "../" + self.settings.handouts_path), 10)
                self.timed_cmd(("mv" + " " + current_chapter + "-6pp" + ".pdf"
                        + " " + "../" + self.settings.handouts_path), 10)
                self.cleanup()
            except OSError:
                print("Error: unable to open test folder")
                print("Check your config file")
                failed_builds_list.append(current_chapter)
                failed_builds_counter = failed_builds_counter + 1
            try:
                os.chdir(self.settings.script_path)
            except OSError:
                print("Error: unable to open the script folder")
                print("This should never happen...")
                FAILED_BUILD_COUNTER = FAILED_BUILD_COUNTER + 1

    def timed_cmd(self, command, timeout):
        """Call a cmd and kill it after 'timeout' seconds"""
        cmd = command.split(" ")
        #TODO: enable this
        self.print_progress_counter()
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
                self.settings.failed_builds_counter = self.settings.failed_builds_counter + 1
                return None
            time.sleep(0.01)
        return process.poll()

    def build_book(self, book_title):
        """Build the handouts book"""
        try:
            os.chdir(self.settings.handouts_path)
            self.timed_cmd(("pdflatex" + " " + book_title), 10)
            self.timed_cmd(("pdflatex" + " " + book_title), 10)
            self.cleanup()
            os.chdir(self.settings.script_path)
        except OSError:
            print("Error: unable build the final book")
            FAILED_BUILDS.append("The book:" + book_title)

    def create_archive(self):
        """Build the archive with all slides and the book"""
        try:
            #TODO: why twice chdir ???
            os.chdir(self.settings.script_path)
            os.chdir(self.settings.handouts_path)
            compression = zipfile.ZIP_DEFLATED
            archive = zipfile.ZipFile(self.settings.archive_title, mode='w')
            try:
                for current_chapter in self.chapters_list:
                    archive.write(current_chapter + ".pdf",
                        compress_type=compression)
                    if(self.settings.build_presentation_slides):
                        archive.write(current_chapter
                            + self.settings.presentation_suffix + ".pdf",
                            compress_type=compression)
                    if(self.settings.cleanup):
                        self.clean_chapter_pdf_files(current_chapter)
                if(self.settings.build_handouts):
                    archive.write(self.settings.book_title + ".pdf",
                        compress_type=compression)
                if(self.settings.build_handouts_notes):
                    archive.write(self.settings.book_title_notes + ".pdf",
                        compress_type=compression)
                if(self.settings.build_handouts_2pp):
                    archive.write(self.settings.book_title_2pp + ".pdf",
                        compress_type=compression)
                if(self.settings.cleanup):
                    self.clean_book_pdf_files()
            finally:
                archive.close()
        except OSError:
            print("Error: unable build the archive: "
                + self.settings.archive_title)
            FAILED_BUILDS.append("Failed to build archive:"
                + self.settings.archive_title)

    def clean_chapter_pdf_files(self, chapter):
        """ Remove temporary pdf files in handouts folder (chapter slides) """
        os.remove(chapter + ".pdf")
        os.remove(chapter + "_2pp.pdf")
        os.remove(chapter + "-6pp.pdf")
        os.remove(chapter + self.settings.notes_suffix + ".pdf")
        os.remove(chapter + self.settings.presentation_suffix + ".pdf")

    def clean_book_pdf_files(self):
        """ Remove temporary pdf files in handouts folder (books) """
        os.remove(self.settings.book_title + ".pdf")
        os.remove(self.settings.book_title_notes + ".pdf")
        os.remove(self.settings.book_title_2pp + ".pdf")

    def cleanup(self):
        """ Clean temporary files
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

    def print_progress_counter(self):
        """ Print the progress counter (e.g. 1/5, 2/5, ...) """
        self.current_task_counter = self.current_task_counter + 1
        print (self.current_task_counter, end="/")
        print (self.total_tasks_counter, end=" ")

    def calculate_total_tasks(self):
        """ Calculate correct counter values based on enabled build options """
        if (self.settings.build_handouts):
            self.total_tasks_counter = self.total_tasks_counter + 5 * self.chapter_counter + 2
        if (self.settings.build_handouts_2pp):
            self.total_tasks_counter = self.total_tasks_counter + 4 * self.chapter_counter + 2
        if (self.settings.build_handouts_notes):
            self.total_tasks_counter = self.total_tasks_counter + 4 * self.chapter_counter + 2
        if (self.settings.build_presentation_slides):
            self.total_tasks_counter = self.total_tasks_counter + 4 * self.chapter_counter

def run():
    """ Run the main program """
    handouts_builder = HandoutsBuilder()
    handouts_builder.run()
    return(handouts_builder.exit_value())

if __name__ == "__main__":
    sys.exit(run())
