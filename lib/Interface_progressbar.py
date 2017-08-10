from tkinter import *
from ttk import Progressbar

# module for progressbar class


class ProgressbarFrame(Frame):
    def __init__(self, parent, progress_var):
        Frame.__init__(self, parent)

        progress_label = Label(self, text="Progress:")
        progress_label.pack(side=LEFT, anchor=CENTER, padx=12, pady=3)

        self.progressbar = Progressbar(self, length=903, variable=progress_var)
        self.progressbar.pack(side=RIGHT, padx=6)
