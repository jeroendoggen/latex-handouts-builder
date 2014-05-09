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
import hashlib

import ConfigParser

from os.path import normpath, walk, isdir, isfile, dirname, basename, \
    exists as path_exists, join as path_join


class Settings:
    """ Contains all the tools to analyse Blackboard assignments """

    Config = ConfigParser.ConfigParser()
    Log = ConfigParser.ConfigParser()
    working_dir = os.getcwd()
    chapters_list = []
    chapters_checksum_list = []
    failed_builds_counter = 0

    def __init__(self):
        self.read_config_file("build.conf")
        self.read_logfile(self.logfile)

    def config_section_map(self, section):
        """ Helper function to read config settings """
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except AttributeError:
                print("exception on %s!" % option)
                dict1[option] = None
                sys.exit(self.failed_builds_counter)
        return dict1

    def read_config_file(self, filename):
        """ Read the config  """
        try:
            self.Config.read(filename)
            self.logfile = self.config_section_map("FileNames")['logfile']
            self.config_file = self.config_section_map("FileNames")['config_file']
            self.book_title = self.config_section_map("FileNames")['book_title']
            self.book_title_notes = self.config_section_map("FileNames")['book_title_notes']
            self.book_title_2pp = self.config_section_map("FileNames")['book_title_2pp']
            self.archive_title = self.config_section_map("FileNames")['archive_title']

            self.build_handouts = self.config_section_map("BuildOptions")['build_handouts']
            self.build_handouts_2pp = self.config_section_map("BuildOptions")['build_handouts_2pp']
            self.build_handouts_notes = self.config_section_map("BuildOptions")['build_handouts_notes']
            self.build_presentation_slides = self.config_section_map("BuildOptions")['build_presentation_slides']
            self.cleanup_pdf_book = self.config_section_map("BuildOptions")['cleanup_pdf_book']
            self.cleanup_pdf_chapters = self.config_section_map("BuildOptions")['cleanup_pdf_chapters']
            self.timeout = self.config_section_map("BuildOptions")['timeout']
            self.build_all = self.config_section_map("BuildOptions")['build_all']

            self.handouts_path = self.config_section_map("Folders")['handouts_path']
            self.archive_title = self.config_section_map("FileNames")['archive_title']

            self.notes_suffix = self.config_section_map("InternalFileNames")['notes_suffix']
            self.two_per_page_suffix = self.config_section_map("InternalFileNames")['two_per_page_suffix']
            self.presentation_suffix = self.config_section_map("InternalFileNames")['presentation_suffix']

            for number, chapter in enumerate(self.Config.items("Chapters")):
                self.chapters_list.append(chapter[1])
        except AttributeError:
            #TODO: this does not work!! (AttributeError or KeyError needed? both?)
            print("Error while processing build.conf")
            self.failed_builds_counter += 1
            sys.exit(self.failed_builds_counter)

    def read_logfile(self, filename):
        """ Read the logfile to get the previous checksum values for all chapters """
        try:
            self.Log.read(filename)
            for chapter in enumerate(self.Log.items("Chapters")):
                #print(chapter[1])
                self.chapters_checksum_list.append(chapter[1])

        except AttributeError:
            #TODO: this does not work!! (AttributeError or KeyError needed? both?)
            print("Error while processing build.conf")
            self.failed_builds_counter += 1
            sys.exit(self.failed_builds_counter)


class HandoutsBuilder:
    """ Contains all the tools to build the LaTeX beamer based handouts """
    chapter_counter = 0
    failed_builds_counter = 0
    failed_builds_list = []
    total_tasks_counter = 0
    current_task_counter = 0
    changed_chapters_list = []
    pdflatex_warnings = 0
    stop_time = 0
    start_time = 0

    def __init__(self):
        """ Initialisations"""
        self.settings = Settings()
        self.chapters_list = self.settings.chapters_list
        #self.reporter = Reporter(self.settings)

    def run(self):
        """ Run the actual program (call this from main) """
        self.timing("start")
        #self.get_chapters_list(self.settings.config_file)
        self.count_total_chapters()
        self.print_chapters(self.settings.book_title)
        self.calculate_total_tasks()
        if(self.settings.build_all == 'True'):
            print("Building all chapters")
            # This could be disabled (but might be useful in some cases)
            self.detect_changed_chapters()
            self.build_handouts(self.chapters_list)
        else:
            print("Skipping chapters without changes")
            self.detect_changed_chapters()
            self.build_handouts(self.changed_chapters_list)
        self.create_archive()
        #self.print_summary(timing("stop"))
        return(0)

    def exit_value(self):
        """ Should return zero when no error are encountered """
        return self.failed_builds_counter

    def detect_changed_chapters(self):
        """ Detect chapters without file changes to speed up build time """
        logfile = open(self.settings.logfile, "w")
        logfile.write("[Chapters]" + "\n")
        previous_checksum_counter = 0
        for chapter_info in enumerate(self.settings.chapters_checksum_list):
            previous_checksum_counter = chapter_info[0]
            print(previous_checksum_counter)
        for number, chapter in enumerate(self.chapters_list):
            current_checksum = path_checksum(['./' + chapter])
            if (number <= previous_checksum_counter):
                previous_checksum = 0
                if (previous_checksum_counter != 0):
                    previous_checksum = self.settings.chapters_checksum_list[number]
            else:
                previous_checksum = 0
            if (current_checksum == previous_checksum):
                if(self.settings.build_all == 'True'):
                    print(chapter + ": No changes, chapter could have been skipped by disabling 'build_all'")
                else:
                    print(chapter + ": No changes, skipping chapter")
                    #TODO: check if all pdf files exists (build will fail if they have been manually deleted from the handouts folder)
            else:
                self.changed_chapters_list.append(chapter)
                #print(self.changed_chapters_list)
            logfile.write(chapter + ": " + str(current_checksum) + "\n")
        print("")
        logfile.close()

    def timing(self, action):
        """Calculate the runtime of the program in seconds """
        if action == "start":
            self.start_time = datetime.datetime.now()
        if action == "stop":
            self.stop_time = datetime.datetime.now()
            passedtime = self.stop_time - self.start_time
            return (passedtime.seconds)

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

    def build_handouts(self, chapters_list):
        """ Build the actual handouts """
        #TODO: this does not work! (reading string from 'settings' -> not boolean)
        if(self.settings.build_handouts == 'True'):
            self.build_chapters(chapters_list, "default")
            self.build_book(self.settings.book_title)
        if(self.settings.build_handouts_notes == 'True'):
            self.build_chapters(chapters_list, self.settings.notes_suffix)
            self.build_book(self.settings.book_title_notes)
        if(self.settings.build_handouts_2pp == 'True'):
            self.build_chapters(chapters_list,
                self.settings.two_per_page_suffix)
            self.build_book(self.settings.book_title_2pp)
        if(self.settings.build_presentation_slides == 'True'):
            self.build_chapters(chapters_list,
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
                self.timed_cmd(("pdflatex" + " " + current_chapter), self.settings.timeout)
                warnings_counter = self.timed_cmd(("pdflatex" + " " + current_chapter), self.settings.timeout)
                self.print_warning_message(current_chapter, warnings_counter)
                if chapter_type == "default":
                    warnings_counter = self.timed_cmd(("pdfjam-slides6up"
                            + " " + current_chapter + ".pdf "
                            + "--nup 2x3 --suffix 6pp -q "), self.settings.timeout)
                    self.print_warning_message(current_chapter, warnings_counter)
                self.timed_cmd(("mv" + " " + current_chapter + ".pdf"
                        + " " + "../" + self.settings.handouts_path), self.settings.timeout)
                self.timed_cmd(("mv" + " " + current_chapter + "-6pp" + ".pdf"
                        + " " + "../" + self.settings.handouts_path), self.settings.timeout)
                self.cleanup()
            except OSError:
                print("Error: unable to open folder: " + current_chapter)
                print("Check your config file")
                self.failed_builds_list.append(current_chapter)
                self.failed_builds_counter += 1
                sys.exit(self.failed_builds_counter)
            try:
                os.chdir(self.settings.working_dir)
            except OSError:
                print("Error: unable to open the script folder: " + self.settings.working_dir)
                print("This should never happen...")
                self.failed_builds_counter += 1
                self.failed_builds_list.append(current_chapter)
                sys.exit(self.failed_builds_counter)

    def print_warning_message(self, command, counter):
        """ Print 'warning message' to cli, can be parsed by Jenkins (CLANG plugin) """ 
        temp = counter + 1
        while counter > 0:
            print (command + ".tex:" + str(temp - counter) + ": warning: pdflatex problem ")
            counter -= 1

    def timed_cmd(self, command, timeout):
        """Call a cmd and kill it after 'timeout' seconds"""
        cmd = command.split(" ")
        self.print_progress_counter()
        print (command)
        start = datetime.datetime.now()
        process = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = process.communicate()
        warnings = out.count('Warning:')

        while process.poll() is None:
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                print ("Process timeout")
                os.kill(process.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                self.failed_builds_counter += 1
                self.failed_builds_list.append(command)
                return None
            time.sleep(0.01)
        return warnings

    def build_book(self, book_title):
        """Build the handouts book"""
        try:
            os.chdir(self.settings.handouts_path)
            self.timed_cmd(("pdflatex" + " " + book_title), self.settings.timeout)
            warnings_counter = self.timed_cmd(("pdflatex" + " " + book_title), self.settings.timeout)
            self.print_warning_message(book_title, warnings_counter)
            self.cleanup()
            os.chdir(self.settings.working_dir)
        except OSError:
            print("Error: unable build the final book")
            self.failed_builds_list.append("The book:" + book_title)
            self.failed_builds_counter += 1
            sys.exit(self.failed_builds_counter)

    def create_archive(self):
        """Build the archive with all slides and the book"""
        try:
            #TODO: why twice chdir ???
            os.chdir(self.settings.working_dir)
            os.chdir(self.settings.handouts_path)
            compression = zipfile.ZIP_DEFLATED
            archive = zipfile.ZipFile(self.settings.archive_title, mode='w')
            try:
                for current_chapter in self.chapters_list:
                    if(self.settings.build_handouts == 'True'):
                        archive.write(current_chapter + ".pdf",
                            compress_type=compression)
                    if(self.settings.build_presentation_slides == 'True'):
                        archive.write(current_chapter
                            + self.settings.presentation_suffix + ".pdf",
                            compress_type=compression)
                    if(self.settings.cleanup_pdf_chapters == 'True'):
                        self.clean_chapter_pdf_files(current_chapter)
                if(self.settings.build_handouts == 'True'):
                    archive.write(self.settings.book_title + ".pdf",
                        compress_type=compression)
                if(self.settings.build_handouts_notes == 'True'):
                    archive.write(self.settings.book_title_notes + ".pdf",
                        compress_type=compression)
                if(self.settings.build_handouts_2pp == 'True'):
                    archive.write(self.settings.book_title_2pp + ".pdf",
                        compress_type=compression)
                if(self.settings.cleanup_pdf_book == 'True'):
                    self.clean_book_pdf_files()
            finally:
                archive.close()
        except OSError:
            print("Error: unable build the archive: "
                + self.settings.archive_title)
            self.failed_builds_list.append("Failed to build archive:"
                + self.settings.archive_title)
            self.failed_builds_counter += 1
            sys.exit(self.failed_builds_counter)

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
        if (self.settings.build_handouts == 'True'):
            self.total_tasks_counter = self.total_tasks_counter + 5 * self.chapter_counter + 2
        if (self.settings.build_handouts_2pp == 'True'):
            self.total_tasks_counter = self.total_tasks_counter + 4 * self.chapter_counter + 2
        if (self.settings.build_handouts_notes == 'True'):
            self.total_tasks_counter = self.total_tasks_counter + 4 * self.chapter_counter + 2
        if (self.settings.build_presentation_slides == 'True'):
            self.total_tasks_counter = self.total_tasks_counter + 4 * self.chapter_counter

    def summary(self):
        """ Print a summary of the build process """
        if(self.failed_builds_counter > 0):
            print("Failed builds: ")
            print(self.failed_builds_list)
            print(", ".join(self.failed_builds_list))


def run():
    """ Run the main program """
    handouts_builder = HandoutsBuilder()
    handouts_builder.run()
    handouts_builder.summary()
    return(handouts_builder.exit_value())


def path_checksum(paths):
    """
        Recursively calculates a checksum representing the contents of all
        files found with a sequence of file and/or directory paths.
        http://code.activestate.com/recipes/576973-getting-the-sha-1-or-md5-hash-of-a-directory/
    """
    if not hasattr(paths, '__iter__'):
        self.failed_builds_counter += 1
        raise TypeError('sequence or iterable expected not %r!' % type(paths))

    def _update_checksum(checksum, dirname, filenames):
        """ Update the checksum for a file """
        for filename in sorted(filenames):
            path = path_join(dirname, filename)
            if isfile(path):
                #print path
                file_handler = open(path, 'rb')
                while 1:
                    buf = file_handler.read(4096)
                    if not buf:
                        break
                    checksum.update(buf)
                file_handler.close()

    chksum = hashlib.sha1()

    for path in sorted([normpath(f) for f in paths]):
        if path_exists(path):
            if isdir(path):
                walk(path, _update_checksum, chksum)
            elif isfile(path):
                _update_checksum(chksum, dirname(path), basename(path))

    return chksum.hexdigest()

if __name__ == "__main__":
    #print (path_checksum(['./chap2']))
    sys.exit(run())
