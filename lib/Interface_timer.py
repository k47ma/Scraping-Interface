# coding=utf-8
import threading
from time import sleep
from tkinter import *
from QA_util import entry_print

# module for timer frame


# frame for containing timer
class TimerFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.thread = None
        self.checking_thread = None
        self.timing = False

        lbl1 = Label(self, text="Time Elapsed: ")
        lbl1.pack(side=LEFT, anchor=CENTER, padx=12)

        self.time_frame = Frame(self)
        self.time_frame.pack(side=LEFT)

        self.hour = Label(self.time_frame, text="00")
        self.hour.pack(side=LEFT)

        colon1 = Label(self.time_frame, text=":")
        colon1.pack(side=LEFT)

        self.minute = Label(self.time_frame, text="00")
        self.minute.pack(side=LEFT)

        colon2 = Label(self.time_frame, text=":")
        colon2.pack(side=LEFT)

        self.second = Label(self.time_frame, text="00")
        self.second.pack(side=LEFT)

    def clear(self):
        self.hour["text"] = "00"
        self.minute["text"] = "00"
        self.second["text"] = "00"

    def start(self):
        self.clear()
        self.thread = TimeThread(hour=self.hour, minute=self.minute, second=self.second, controller=self.checking_thread)
        self.thread.daemon = True
        self.timing = True
        self.thread.start()

    def stop(self):
        self.timing = False


# thread for timing and updating timer
class TimeThread(threading.Thread):
    def __init__(self, hour, minute, second, controller):
        threading.Thread.__init__(self)

        self.hour = hour
        self.minute = minute
        self.second = second
        self.controller = controller

    def run(self):
        hour_var = 0
        minute_var = 0
        second_var = 0

        while self.controller.isAlive():
            sleep(1)
            second_var += 1

            # if second reaches 60
            if second_var == 60:
                second_var = 0
                minute_var += 1

            # if minute reaches 60
            if minute_var == 60:
                minute_var = 0
                hour_var += 1

            try:
                self.update(hour_var, minute_var, second_var)
            except TclError:
                continue
        entry_print("Process finished in %d h %d min %d s." % (hour_var, minute_var, second_var))

    def update(self, hour, minute, second):
        self.hour["text"] = "%02d" % hour
        self.minute["text"] = "%02d" % minute
        self.second["text"] = "%02d" % second
