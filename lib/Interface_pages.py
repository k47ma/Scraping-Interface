# coding=utf-8
import tkFont
import tkMessageBox
from QA_util import clear_all
from config import *
from Interface_event import *
from Interface_thread import *
from Interface_timer import TimerFrame
from Interface_progressbar import ProgressbarFrame
from Interface_util import ask_quit
from Interface_settings import *

# module for page classes


root = None


# class for the tk window
class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        global root
        root = self

        status["INTERFACE_MODE"] = True

        root.iconbitmap(r'image\icon.ico')
        self.protocol("WM_DELETE_WINDOW", ask_quit)
        self.wm_title("QA Interface")
        self.wm_geometry("1000x600")
        self.minsize(width=500, height=300)
        self["cursor"] = "@main.cur"

        load_config()

        self.customFont = tkFont.Font(family="Helvetica", size=12)

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {}

        startpage = StartPage(parent=container, controller=self)
        self.pages["startpage"] = startpage
        startpage.grid(row=0, column=0, sticky=NSEW)

        page1 = Page1(parent=container, controller=self)
        self.pages["page1"] = page1
        page1.grid(row=0, column=0, sticky=NSEW)

        page2 = Page2(parent=container, controller=self)
        self.pages["page2"] = page2
        page2.grid(row=0, column=0, sticky=NSEW)

        page3 = Page3(parent=container, controller=self)
        self.pages["page3"] = page3
        page3.grid(row=0, column=0, sticky=NSEW)

        page4 = Page4(parent=container, controller=self)
        self.pages["page4"] = page4
        page4.grid(row=0, column=0, sticky=NSEW)

        page5 = Page5(parent=container, controller=self)
        self.pages["page5"] = page5
        page5.grid(row=0, column=0, sticky=NSEW)

        page6 = Page6(parent=container, controller=self)
        self.pages["page6"] = page6
        page6.grid(row=0, column=0, sticky=NSEW)

        page7 = Page7(parent=container, controller=self)
        self.pages["page7"] = page7
        page7.grid(row=0, column=0, sticky=NSEW)

        page8 = Page8(parent=container, controller=self)
        self.pages["page8"] = page8
        page8.grid(row=0, column=0, sticky=NSEW)

        self.show_frame("startpage")

    def show_frame(self, name):
        frame = self.pages.get(name)
        frame.lift()
        if name == "startpage":
            self.wm_title("QA Interface")
        elif name == "page1":
            self.wm_title("QA Interface - Single Site")
        elif name == "page2":
            self.wm_title("QA Interface - Multiple Sites")
        elif name == "page3":
            self.wm_title("QA Interface - Single Site with Login")
        elif name == "page4":
            self.wm_title("QA Interface - Multiple Sites with Login")
        elif name == "page5":
            self.wm_title("QA Interface - Page Structure Migration")
        elif name == "page6":
            self.wm_title("QA Interface - Metadata Migration")
        elif name == "page7":
            self.wm_title("QA Interface - Blog Migration")
        elif name == "page8":
            self.wm_title("QA Interface - Site Migration")
        elif name == "page9":
            self.wm_title("QA Interface - Image Migration")
        elif name == "page10":
            self.wm_title("QA Interface - Content Migration")
        elif name == "page11":
            self.wm_title("QA Interface - Metadata Migration")


# class for start page frame
class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        qa_frame = LabelFrame(self, text="QA Options")
        qa_frame.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=6)

        migrate_frame_main = Frame(self)
        migrate_frame_main.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=6)

        migrate_frame_main.columnconfigure(0, weight=1)
        migrate_frame_main.columnconfigure(1, weight=1)

        migrate_frame1 = LabelFrame(migrate_frame_main, text="Migration Options with Selenium")
        migrate_frame1.grid(row=0, column=0, sticky=NSEW, padx=(0, 6))

        migrate_frame2 = LabelFrame(migrate_frame_main, text="Migration Options with Python")
        migrate_frame2.grid(row=0, column=1, sticky=NSEW, padx=(6, 0))

        btn_frame = Frame(self)
        btn_frame.pack(side=BOTTOM, fill=X, expand=False)

        self.setting_icon = PhotoImage(file="image\\setting.gif")

        setting = Button(qa_frame, image=self.setting_icon, command=self.show_settings)
        setting.pack(anchor=NE, padx=5, pady=5)

        p1btn = Button(qa_frame, text="Compare Single Site", width=30, height=2,
                       command=lambda: controller.show_frame("page1"))
        p1btn.pack(side=TOP, padx=5, pady=(10, 5))
        p1btn.bind("<Enter>", on_enter)
        p1btn.bind("<Leave>", on_leave)
        p1btn.bind("<ButtonRelease-1>", on_enter)

        p2btn = Button(qa_frame, text="Compare Multiple Sites", width=30, height=2,
                       command=lambda: controller.show_frame("page2"))
        p2btn.pack(side=TOP, padx=5, pady=5)
        p2btn.bind("<Enter>", on_enter)
        p2btn.bind("<Leave>", on_leave)
        p2btn.bind("<ButtonRelease-1>", on_enter)

        p3btn = Button(qa_frame, text="Compare Single Site with Login", width=30, height=2,
                       command=lambda: controller.show_frame("page3"))
        p3btn.pack(side=TOP, padx=5, pady=5)
        p3btn.bind("<Enter>", on_enter)
        p3btn.bind("<Leave>", on_leave)
        p3btn.bind("<ButtonRelease-1>", on_enter)

        p4btn = Button(qa_frame, text="Compare Multiple Sites with Login", width=30, height=2,
                       command=lambda: controller.show_frame("page4"))
        p4btn.pack(side=TOP, padx=5, pady=(5, 10))
        p4btn.bind("<Enter>", on_enter)
        p4btn.bind("<Leave>", on_leave)
        p4btn.bind("<ButtonRelease-1>", on_enter)

        p5btn = Button(migrate_frame1, text="Create Subpages (Essentials Only)", width=30, height=2,
                       command=lambda: controller.show_frame("page5"))
        p5btn.pack(side=TOP, padx=5, pady=(5, 5))
        p5btn.bind("<Enter>", on_enter)
        p5btn.bind("<Leave>", on_leave)
        p5btn.bind("<ButtonRelease-1>", on_enter)

        p6btn = Button(migrate_frame1, text="Migrate Metadata", width=30, height=2,
                       command=lambda: controller.show_frame("page6"))
        p6btn.pack(side=TOP, padx=5, pady=(5, 5))
        p6btn.bind("<Enter>", on_enter)
        p6btn.bind("<Leave>", on_leave)
        p6btn.bind("<ButtonRelease-1>", on_enter)

        p7btn = Button(migrate_frame1, text="Migrate Blog", width=30, height=2,
                       command=lambda: controller.show_frame("page7"))
        p7btn.pack(side=TOP, padx=5, pady=(5, 5))
        p7btn.bind("<Enter>", on_enter)
        p7btn.bind("<Leave>", on_leave)
        p7btn.bind("<ButtonRelease-1>", on_enter)

        p8btn = Button(migrate_frame2, text="Migrate Site", width=30, height=2,
                       command=lambda: controller.show_frame("page8"))
        p8btn.pack(side=TOP, padx=5, pady=(5, 5))
        p8btn.bind("<Enter>", on_enter)
        p8btn.bind("<Leave>", on_leave)
        p8btn.bind("<ButtonRelease-1>", on_enter)

        p9btn = Button(migrate_frame2, text="Migrate Images", width=30, height=2,
                       command=lambda: controller.show_frame("page9"))
        p9btn.pack(side=TOP, padx=5, pady=(5, 5))
        p9btn.bind("<Enter>", on_enter)
        p9btn.bind("<Leave>", on_leave)
        p9btn.bind("<ButtonRelease-1>", on_enter)

        p10btn = Button(migrate_frame2, text="Migrate Content", width=30, height=2,
                        command=lambda: controller.show_frame("page10"))
        p10btn.pack(side=TOP, padx=5, pady=(5, 5))
        p10btn.bind("<Enter>", on_enter)
        p10btn.bind("<Leave>", on_leave)
        p10btn.bind("<ButtonRelease-1>", on_enter)

        p11btn = Button(migrate_frame2, text="Migrate Metadata", width=30, height=2,
                        command=lambda: controller.show_frame("page11"))
        p11btn.pack(side=TOP, padx=5, pady=(5, 20))
        p11btn.bind("<Enter>", on_enter)
        p11btn.bind("<Leave>", on_leave)
        p11btn.bind("<ButtonRelease-1>", on_enter)

        self.quit_icon = PhotoImage(file="image\\exit.gif")

        quitbtn = Button(btn_frame, text="QUIT", image=self.quit_icon, compound=RIGHT, fg="red", command=ask_quit)
        quitbtn.pack(side=RIGHT, expand=False, padx=5, pady=5)

    def show_settings(self):
        SettingWindow()


# class for "checking single site" frame
class Page1(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old URL", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New URL", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.clear_history_var = IntVar()
        self.clear_history_var.set(1)

        clear_history = Checkbutton(util_frame, text="Clear history before checking", variable=self.clear_history_var,
                                    underline=0)
        clear_history.pack(side=RIGHT, padx=6)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_icon = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6, ipadx=2)

        back_btn = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        back_btn.pack(side=LEFT, padx=5, pady=5, ipadx=2)

    def start(self, *args):
        if not self.entry1.get() or not self.entry2.get():
            tkMessageBox.showinfo("URL Required", "Old URL and New URL are required!")
            return

        status["CURRENT_ENTRY"] = self.result
        status["CHECKING_STATUS"] = True
        self.progress_var.set(0)

        self.start_btn.configure(text="STOP", image=self.stop_icon, command=self.stop, fg="red")

        if self.clear_history_var.get():
            clear_all()
            self.result.delete('1.0', END)

        old_url = self.entry1.get()
        new_url = self.entry2.get()

        self.result.insert(END, "-----------------------------------------------------\nStart checking...\n")
        thread = CompareThread(old_url, new_url, self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# class for "checking multiple sites" frame
class Page2(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.clear_history_var = IntVar()
        self.clear_history_var.set(1)

        clear_history = Checkbutton(util_frame, text="Clear history before checking", variable=self.clear_history_var,
                                    underline=0)
        clear_history.pack(side=RIGHT, padx=6)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=BOTH, expand=True)

        lbl1 = Label(frame1, text="File Path", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.fname = StringVar()

        self.fname_entry = Entry(frame1, textvariable=self.fname)
        self.fname_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        self.fname_entry.bind("<FocusIn>", on_focusin)
        self.fname_entry.bind("<FocusOut>", on_focusout)

        browse_btn = Button(frame1, text="Browse", command=self.load_file, width=10)
        browse_btn.pack(side=RIGHT, padx=5, pady=5, anchor=E)

        lbl2 = Label(frame2, text="Result", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame2)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame3 = Frame(self)
        frame3.pack(fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame3, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_icon = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame3, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        back_btn = Button(frame3, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        back_btn.pack(side=LEFT, padx=6, pady=6)

    def load_file(self):
        file = askopenfilename(filetypes=(("CSV files", "*.csv"),))
        if file:
            self.fname.set(file)
        return

    def start(self):
        if not self.fname_entry.get():
            tkMessageBox.showinfo("File Path Required", "File Path is required!")
            return

        status["CURRENT_ENTRY"] = self.result
        status["CHECKING_STATUS"] = True
        self.progress_var.set(0)

        self.start_btn.configure(text="STOP", image=self.stop_icon, command=self.stop, fg="red")

        if self.clear_history_var.get():
            clear_all()
            self.result.delete('1.0', END)

        self.result.insert(END, "-----------------------------------------------------\nStart checking...\n")
        fname = self.fname_entry.get()
        thread = CompareCSVThread(fname, self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# class for "checking single site with login" frame
class Page3(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old URL", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New URL", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.clear_history_var = IntVar()
        self.clear_history_var.set(1)

        clear_history = Checkbutton(util_frame, text="Clear history before checking", variable=self.clear_history_var,
                                    underline=0)
        clear_history.pack(side=RIGHT, padx=6)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame3 = Frame(self)
        frame3.pack(side=TOP, fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_icon = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        quit_btn = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        quit_btn.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not os.path.isfile(settings["EXECUTABLE_PATH"]):
            tkMessageBox.showinfo("Chromedriver File Does Not Exist",
                                  "Path for Chromedriver is invalid or file does not exist.\nPlease check your setting.")
            return

        if not self.entry1.get() or not self.entry2.get():
            tkMessageBox.showinfo("URL Required", "Old URL and New URL are required fields!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result
        status["CHECKING_STATUS"] = True
        self.progress_var.set(0)

        self.start_btn.configure(text="STOP", image=self.stop_icon, command=self.stop, fg="red")

        if self.clear_history_var.get():
            clear_all()
            self.result.delete('1.0', END)

        self.result.insert(END, "-----------------------------------------------------\nStart checking...\n")

        thread = CompareSeleniumThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def login_setting(self):
        LoginWindow(self)

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# class for "checking multiple sites with login" frame
class Page4(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.clear_history_var = IntVar()
        self.clear_history_var.set(1)

        clear_history = Checkbutton(util_frame, text="Clear history before checking", variable=self.clear_history_var,
                                    underline=0)
        clear_history.pack(side=RIGHT, padx=6)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=BOTH, expand=True)

        lbl1 = Label(frame1, text="File Path", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.fname = StringVar()

        self.fname_entry = Entry(frame1, textvariable=self.fname)
        self.fname_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        self.fname_entry.bind("<FocusIn>", on_focusin)
        self.fname_entry.bind("<FocusOut>", on_focusout)

        browse_btn = Button(frame1, text="Browse", command=self.load_file, width=10)
        browse_btn.pack(side=RIGHT, padx=5, pady=5, anchor=E)

        lbl2 = Label(frame2, text="Result", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame2)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_icon = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        back_btn = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        back_btn.pack(side=LEFT, padx=6, pady=6)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def load_file(self):
        file = askopenfilename(filetypes=(("CSV files", "*.csv"),))
        if file:
            self.fname.set(file)
        return

    def start(self):
        if not self.fname_entry.get():
            tkMessageBox.showinfo("File Path Required", "File Path is required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result
        status["CHECKING_STATUS"] = True
        self.progress_var.set(0)

        self.start_btn.configure(text="STOP", image=self.stop_icon, command=self.stop, fg="red")

        if self.clear_history_var.get():
            clear_all()
            self.result.delete('1.0', END)

        self.result.insert(END, "-----------------------------------------------------\nStart checking...\n")
        fname = self.fname_entry.get()
        thread = CompareSeleniumCSVThread(fname, self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def login_setting(self):
        LoginWindow(self)

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# class for "create subpages" frame
class Page5(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old URL", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New URL", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_icon = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        back_btn = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        back_btn.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get() or not self.entry2.get():
            tkMessageBox.showinfo("URL Required", "Old URL and New URL are required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result
        status["CHECKING_STATUS"] = True
        self.progress_var.set(0)

        self.start_btn.configure(text="STOP", image=self.stop_icon, command=self.stop, fg="red")

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = CreateSubpageThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def login_setting(self):
        LoginWindow(self)

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# class for "migrate metadata" frame
class Page6(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old URL", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New URL", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_icon = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        back_btn = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        back_btn.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get() or not self.entry2.get():
            tkMessageBox.showinfo("URL Required", "Old URL and New URL are required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result
        status["CHECKING_STATUS"] = True
        self.progress_var.set(0)

        self.start_btn.configure(text="STOP", image=self.stop_icon, command=self.stop, fg="red")

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = MigrateMetaThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def login_setting(self):
        LoginWindow(self)

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# class for "migrate blog" frame
class Page7(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old Blog", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New Blog", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        self.progress_var = DoubleVar()
        self.progress_frame = ProgressbarFrame(self, self.progress_var)
        self.progress_frame.pack(side=TOP, fill=X)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)
        self.result.bind("<Configure>", self.resize)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_btn = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        button3 = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        button3.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get() or not self.entry2.get():
            tkMessageBox.showinfo("URL Required", "Old URL and New URL are required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result
        self.progress_var.set(0)

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = MigrateBlogThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def stop(self):
        if tkMessageBox.askyesnocancel(title="QA Interface",
                                       message="Are you sure you want to stop the progress?") == YES:
            status["CHECKING_STATUS"] = False
            self.start_btn["state"] = DISABLED

    def login_setting(self):
        LoginWindow(self)

    def resize(self, event):
        self.progress_frame.progressbar["length"] = event.width


# page for site migration
class Page8(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old Site", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New Site", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_btn = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        button3 = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        button3.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get():
            tkMessageBox.showinfo("URL Required", "Old URL is required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = MigrateSiteThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.start_btn["state"] = DISABLED

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def login_setting(self):
        LoginWindow(self)


# page for image migration
class Page9(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old Site", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New Site", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_btn = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        button3 = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        button3.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get():
            tkMessageBox.showinfo("URL Required", "Old URL is required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = MigrateImageThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.start_btn["state"] = DISABLED

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def login_setting(self):
        LoginWindow(self)


# page for content migration
class Page10(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old Site", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New Site", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_btn = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        button3 = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        button3.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get():
            tkMessageBox.showinfo("URL Required", "Old URL is required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = MigrateContentThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.start_btn["state"] = DISABLED

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def login_setting(self):
        LoginWindow(self)


# page for image migration
class Page11(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X)

        lbl1 = Label(frame1, text="Old Site", width=10)
        lbl1.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry1 = Entry(frame1)
        self.entry1.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry1.bind("<Key-Return>", self.start)
        self.entry1.bind("<FocusIn>", on_focusin)
        self.entry1.bind("<FocusOut>", on_focusout)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=X)

        lbl2 = Label(frame2, text="New Site", width=10)
        lbl2.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.entry2 = Entry(frame2)
        self.entry2.pack(side=RIGHT, padx=5, fill=X, expand=True)
        self.entry2.bind("<Key-Return>", self.start)
        self.entry2.bind("<FocusIn>", on_focusin)
        self.entry2.bind("<FocusOut>", on_focusout)

        util_frame = Frame(self)
        util_frame.pack(side=TOP, fill=X)

        self.timer_frame = TimerFrame(util_frame)
        self.timer_frame.pack(side=LEFT, anchor=CENTER)

        frame3 = Frame(self)
        frame3.pack(fill=BOTH, expand=True)

        lbl3 = Label(frame3, text="Result", width=10)
        lbl3.pack(side=LEFT, padx=5, pady=5, anchor=W)

        self.result = Text(frame3)
        self.result.pack(fill=BOTH, padx=5, pady=5, expand=True)

        scrollbar = Scrollbar(self.result, command=self.result.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result["yscrollcommand"] = scrollbar.set

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=X)

        self.quit_icon = PhotoImage(file="image\\exit2.gif")
        quit_btn = Button(frame4, text="QUIT", image=self.quit_icon, compound=LEFT, command=ask_quit, fg="red",
                          font=("Arial", 9, "bold"))
        quit_btn.pack(side=RIGHT, padx=6, pady=6)

        self.start_icon = PhotoImage(file="image\\start.gif")
        self.stop_btn = PhotoImage(file="image\\stop.gif")
        self.start_btn = Button(frame4, text="START", image=self.start_icon, compound=LEFT, command=self.start,
                                fg="#399656", font=("Arial", 9, "bold"))
        self.start_btn.pack(side=RIGHT, padx=6, pady=6)

        button3 = Button(frame4, text="<< BACK", command=lambda: controller.show_frame("startpage"))
        button3.pack(side=LEFT, padx=5, pady=5)

        setting_btn = Button(frame4, text="Login Setting...", command=self.login_setting)
        setting_btn.pack(side=BOTTOM, padx=5, pady=5)

    def start(self, *args):
        if not self.entry1.get():
            tkMessageBox.showinfo("URL Required", "Old URL is required!")
            return

        if not settings["USER_NAME"] or not settings["PASSWORD"]:
            tkMessageBox.showinfo("Login Setting Required", "Please finish login setting first!")
            return

        status["CURRENT_ENTRY"] = self.result

        self.result.insert(END, "-----------------------------------------------------\nStart migrating...\n")
        thread = MigrateMetadataThread(self.entry1.get(), self.entry2.get(), self)
        thread.daemon = True

        self.start_btn["state"] = DISABLED

        self.timer_frame.checking_thread = thread

        thread.start()
        self.timer_frame.start()

    def login_setting(self):
        LoginWindow(self)


class LoginWindow(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)

        self.parent = parent

        x = root.winfo_x()
        y = root.winfo_y()

        self.transient(master=parent)
        self.focus()
        self.title("Login Setting")
        self.geometry("250x125+%d+%d" % (x + 125, y + 87.5))
        self.resizable(False, False)

        self.iconbitmap(r'image\icon.ico')

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

        lbl1 = Label(frame1, text="Username:", width=8)
        lbl1.grid(row=0, column=0, padx=6, pady=6)

        lbl2 = Label(frame1, text="Password:", width=8)
        lbl2.grid(row=1, column=0, padx=6, pady=6)

        username = StringVar()
        password = StringVar()

        username.set(settings["USER_NAME"])
        password.set(settings["PASSWORD"])

        self.username_entry = Entry(frame1, width=25, textvariable=username)
        self.username_entry.grid(row=0, column=1, sticky=E + W, padx=6, pady=6)
        self.username_entry.bind("<Key-Return>", self.save)

        self.password_entry = Entry(frame1, show="*", width=25, textvariable=password)
        self.password_entry.grid(row=1, column=1, sticky=E + W, padx=6, pady=6)
        self.password_entry.bind("<Key-Return>", self.save)

        frame2 = Frame(self)
        frame2.pack(side=BOTTOM, fill=X, expand=False)

        save_btn = Button(frame2, text="Save", width=8, height=1, command=self.save)
        save_btn.pack(side=LEFT, padx=(40, 20), pady=10)

        back_btn = Button(frame2, text="Close", width=8, height=1, command=self.destroy)
        back_btn.pack(side=RIGHT, padx=(20, 40), pady=10)

    def save(self, *args):
        data = {'USER_NAME': self.username_entry.get(), 'PASSWORD': self.password_entry.get()}
        save_config(data)
        self.destroy()
