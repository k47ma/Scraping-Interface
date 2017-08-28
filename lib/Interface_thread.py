# coding=utf-8
import threading
from selenium.common.exceptions import NoSuchWindowException
from QA_compare_thread import *
from QA_selenium import *
from Migrator_subpage import migrate_subpages
from Migrator_metadata import migrate_meta
from Migrator_blog import migrate_blog


# module for threading events


class CompareThread(threading.Thread):
    def __init__(self, old_url, new_url, parent):
        threading.Thread.__init__(self)
        self.old_url = old_url
        self.new_url = new_url
        self.parent = parent

    def run(self):
        compare_site_thread(self.old_url, self.new_url, progress_var=self.parent.progress_var, step=100.0)
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False


class CompareCSVThread(threading.Thread):
    def __init__(self, fname, parent):
        threading.Thread.__init__(self)
        self.fname = fname
        self.parent = parent

    def run(self):
        compare_site_thread_csv(self.fname, progress_var=self.parent.progress_var, step=100.0)
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False


class CompareSeleniumThread(threading.Thread):
    def __init__(self, old_url, new_url, parent):
        threading.Thread.__init__(self)
        self.old_url = old_url
        self.new_url = new_url
        self.parent = parent

    def run(self):
        try:
            compare_site_selenium(self.old_url, self.new_url, progress_var=self.parent.progress_var, step=100.0)
        except NoSuchWindowException:
            entry_print("Process interrupted!", True)
            pass
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False


class CompareSeleniumCSVThread(threading.Thread):
    def __init__(self, fname, parent):
        threading.Thread.__init__(self)
        self.fname = fname
        self.parent = parent

    def run(self):
        try:
            compare_site_selenium_csv(self.fname, progress_var=self.parent.progress_var, step=100.0)
        except NoSuchWindowException:
            entry_print("Process interrupted!", True)
            pass
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False


class CreateSubpageThread(threading.Thread):
    def __init__(self, old_url, new_url, parent):
        threading.Thread.__init__(self)
        self.old_url = old_url
        self.new_url = new_url
        self.parent = parent

    def run(self):
        migrate_subpages(self.old_url, self.new_url, progress_var=self.parent.progress_var, step=100.0)
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False


class MigrateMetaThread(threading.Thread):
    def __init__(self, old_url, new_url, parent):
        threading.Thread.__init__(self)
        self.old_url = old_url
        self.new_url = new_url
        self.parent = parent

    def run(self):
        migrate_meta(self.old_url, self.new_url, progress_var=self.parent.progress_var, step=100.0)
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False


class MigrateBlogThread(threading.Thread):
    def __init__(self, old_blog, new_blog, parent):
        threading.Thread.__init__(self)
        self.old_blog = old_blog
        self.new_blog = new_blog
        self.parent = parent

    def run(self):
        migrate_blog(self.old_blog, self.new_blog, progress_var=self.parent.progress_var, step=100.0)
        self.parent.progress_var.set(100.0)
        self.parent.start_btn.configure(text="START", image=self.parent.start_icon, command=self.parent.start,
                                        fg="green", state="normal")
        status["CHECKING_STATUS"] = False
