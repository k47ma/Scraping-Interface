# coding=utf-8
from tkFileDialog import askopenfilename
from tkinter import *
from Interface_config import *
from Interface_unicode import UnicodeLookUpFrame

# module for setting page and frames


class SettingWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)

        self.resizable(width=False, height=False)
        self.iconbitmap(r'image\icon.ico')

        self.wm_title("Settings")
        self.wm_geometry("750x500")

        self.focus()

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X, expand=False)

        lbl1 = Label(frame1, text="Category:")
        lbl1.pack(side=LEFT, padx=6, pady=6)

        options = ["Login", "Chromedriver Path", "Thread Setting", "Page Exception Setting",
                   "Special Character Setting"]
        menu_var = StringVar()
        menu_var.set(options[0])

        menu = OptionMenu(frame1, menu_var, *options, command=self.show_frame)
        menu.pack(side=LEFT, fill=X)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=BOTH, expand=True, padx=6, pady=6)
        frame2.columnconfigure(0, weight=1)
        frame2.rowconfigure(0, weight=1)

        self.pages = {}

        self.login_frame = LoginSetting(parent=frame2, controller=self, text="Login Setting")
        self.pages["Login"] = self.login_frame
        self.login_frame.grid(row=0, column=0, sticky=NSEW)

        self.path_frame = PathSetting(parent=frame2, controller=self, text="Chromedriver Path Setting")
        self.pages["Chromedriver Path"] = self.path_frame
        self.path_frame.grid(row=0, column=0, sticky=NSEW)

        self.threadpool_frame = ThreadPoolSetting(parent=frame2, controller=self, text="Thread Setting")
        self.pages["Thread Setting"] = self.threadpool_frame
        self.threadpool_frame.grid(row=0, column=0, sticky=NSEW)

        self.exception_frame = ExceptionSetting(parent=frame2, controller=self, text="Page Exception Setting")
        self.pages["Page Exception Setting"] = self.exception_frame
        self.exception_frame.grid(row=0, column=0, sticky=NSEW)

        self.special_char_frame = SpecialCharacterSetting(parent=frame2, controller=self,
                                                          text="Special Character Setting")
        self.pages["Special Character Setting"] = self.special_char_frame
        self.special_char_frame.grid(row=0, column=0, sticky=NSEW)

        frame3 = Frame(self, height=1)
        frame3.pack(side=BOTTOM, fill=X, expand=False)

        close_btn = Button(frame3, text="CLOSE", command=self.destroy)
        close_btn.pack(side=LEFT, padx=6, pady=6)

        apply_btn = Button(frame3, text="APPLY", command=self.apply)
        apply_btn.pack(side=RIGHT, padx=6, pady=6)

        save_btn = Button(frame3, text="SAVE", command=self.save)
        save_btn.pack(side=RIGHT, padx=6, pady=6)

        self.show_frame(options[0])

    def show_frame(self, key):
        self.pages[key].lift()

    def apply(self, *args):
        data = self.fetch_data()
        save_config(data)

    def save(self, *args):
        self.apply()
        self.destroy()

    def fetch_data(self):
        data = {}
        for key, value in self.pages.iteritems():
            data.update(value.fetch_data())
        return data


class LoginSetting(LabelFrame):
    def __init__(self, parent, controller, text):
        LabelFrame.__init__(self, parent, text=text)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

        lbl1 = Label(frame1, text="Username:", width=8)
        lbl1.grid(row=0, column=0, padx=6, pady=6)

        lbl2 = Label(frame1, text="Password:", width=8)
        lbl2.grid(row=1, column=0, padx=6, pady=6)

        username = StringVar()
        password = StringVar()

        username.set(config.settings["USER_NAME"])
        password.set(config.settings["PASSWORD"])

        self.username_entry = Entry(frame1, width=25, textvariable=username)
        self.username_entry.grid(row=0, column=1, sticky=E + W, padx=6, pady=6)
        self.username_entry.bind("<Key-Return>", controller.apply)

        self.password_entry = Entry(frame1, show="*", width=25, textvariable=password)
        self.password_entry.grid(row=1, column=1, sticky=E + W, padx=6, pady=6)
        self.password_entry.bind("<Key-Return>", controller.apply)

    def fetch_data(self):
        data = {"USER_NAME": self.username_entry.get(),
                "PASSWORD": self.password_entry.get()}
        return data


class PathSetting(LabelFrame):
    def __init__(self, parent, controller, text):
        LabelFrame.__init__(self, parent, text=text)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)
        frame1.columnconfigure(1, weight=1)

        lbl = Label(frame1, text="Path to chromedriver.eve:")
        lbl.grid(row=0, column=0, padx=6, pady=6)

        self.fname = StringVar()
        self.fname.set(config.settings["EXECUTABLE_PATH"])

        self.path_entry = Entry(frame1, textvariable=self.fname)
        self.path_entry.grid(row=0, column=1, padx=6, pady=6, sticky=E + W)
        self.path_entry.bind("<Key-Return>", controller.apply)

        browse_btn = Button(frame1, text="Browse", command=self.load_file, width=10)
        browse_btn.grid(row=0, column=2, padx=6, pady=6)

    def load_file(self):
        file = askopenfilename(filetypes=(("Executable files", "*.exe"),))
        if file:
            self.focus()
            self.fname.set(file)
        return

    def fetch_data(self):
        data = {"EXECUTABLE_PATH": self.fname.get()}
        return data


class ThreadPoolSetting(LabelFrame):
    def __init__(self, parent, controller, text):
        LabelFrame.__init__(self, parent, text=text)

        lbl1 = Label(self, wraplength=720, justify=LEFT,
                     font=("Times", 12), fg="#4169E1",
                     text="* Threadpool size is the number of pages being checked at the same time. " +
                          "Increasing the value will shorten the time of the process " +
                          "while it might also cause unexpected shutdown of the program " +
                          "due to the unstable performance of threading.")
        lbl1.pack(side=BOTTOM, pady=10)

        frame1 = Frame(self, height=20)
        frame1.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=10)

        lbl2 = Label(frame1, text="Threadpool size:")
        lbl2.grid(row=0, column=0, padx=6, pady=6)

        size_var = StringVar()
        size_var.set(str(config.settings["THREADPOOL_SIZE"]))

        self.selector = Spinbox(frame1, width=5, from_=1, to=50, textvariable=size_var, state="readonly", bd=1)
        self.selector.grid(row=0, column=1, padx=6, pady=6, sticky=NSEW)

        self.msg = Label(frame1, font=("Arial", 10))
        self.msg.grid(row=0, column=2, padx=6, pady=6)

    def fetch_data(self):
        data = {"THREADPOOL_SIZE": int(self.selector.get())}
        return data


class ExceptionSetting(LabelFrame):
    def __init__(self, parent, controller, text):
        LabelFrame.__init__(self, parent, text=text)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=X, expand=False)

        lbl = Label(frame1, text="Type:")
        lbl.pack(side=LEFT, padx=5, pady=5)

        select_var = StringVar()
        options = ["All Old Sites", "All New Sites", "Old Space Page Text Content", "New Space Page Text Content",
                   "Old Space Page Images", "New Space Page Images", "Checking New Images Information",
                   "Old Space Page Links", "New Space Page Links", "Homepage Images (New Site Only)",
                   "Homepage Links (New Site Only)", "Old Homepage Text Content",
                   "New Homepage Text Content", "Old Blog Page Text Content", "New Blog Page Text Content",
                   "Old Blog Page Images", "New Blog Page Images", "Old Blog Page Links", "New Blog Page Links",
                   "Old Forms Page", "New Forms Page"]
        select = OptionMenu(frame1, select_var, *options, command=self.show_frame)
        select.pack(side=LEFT)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=BOTH, expand=True)
        frame2.rowconfigure(0, weight=1)
        frame2.columnconfigure(0, weight=1)

        self.pages = {}

        all_old_sites = ExceptionTypeFrame(parent=frame2, exception_type="GET_OLD_SOUP_IGNORE")
        self.pages["All Old Sites"] = all_old_sites

        all_new_sites = ExceptionTypeFrame(parent=frame2, exception_type="GET_NEW_SOUP_IGNORE")
        self.pages["All New Sites"] = all_new_sites

        old_space_page_text_content = ExceptionTypeFrame(parent=frame2, exception_type="GET_OLD_CONTENT_IGNORE")
        self.pages["Old Space Page Text Content"] = old_space_page_text_content

        new_space_page_text_content = ExceptionTypeFrame(parent=frame2, exception_type="GET_NEW_CONTENT_IGNORE")
        self.pages["New Space Page Text Content"] = new_space_page_text_content

        old_space_page_images = ExceptionTypeFrame(parent=frame2, exception_type="COMPARE_OLD_IMAGE_IGNORE")
        self.pages["Old Space Page Images"] = old_space_page_images

        new_space_page_images = ExceptionTypeFrame(parent=frame2, exception_type="COMPARE_NEW_IMAGE_IGNORE")
        self.pages["New Space Page Images"] = new_space_page_images

        checking_new_images_information = ExceptionTypeFrame(parent=frame2, exception_type="CHECKING_IMAGE_IGNORE")
        self.pages["Checking New Images Information"] = checking_new_images_information

        old_space_page_links = ExceptionTypeFrame(parent=frame2, exception_type="COMPARE_OLD_LINK_IGNORE")
        self.pages["Old Space Page Links"] = old_space_page_links

        new_space_page_links = ExceptionTypeFrame(parent=frame2, exception_type="COMPARE_NEW_LINK_IGNORE")
        self.pages["New Space Page Links"] = new_space_page_links

        homepage_images = ExceptionTypeFrame(parent=frame2, exception_type="HOMEPAGE_IMAGE_IGNORE")
        self.pages["Home Page Images (New Site Only)"] = homepage_images

        homepage_links = ExceptionTypeFrame(parent=frame2, exception_type="HOMEPAGE_LINK_IGNORE")
        self.pages["Home Page Links (New Site Only)"] = homepage_links

        old_homepage_text_content = ExceptionTypeFrame(parent=frame2, exception_type="OLD_HOMEPAGE_CONTENT_IGNORE")
        self.pages["Old Homepage Text Content"] = old_homepage_text_content

        new_homepage_text_content = ExceptionTypeFrame(parent=frame2, exception_type="NEW_HOMEPAGE_CONTENT_IGNORE")
        self.pages["New Homepage Text Content"] = new_homepage_text_content

        old_blog_page_text_content = ExceptionTypeFrame(parent=frame2, exception_type="OLD_BLOG_CONTENT_IGNORE")
        self.pages["Old Blog Page Text Content"] = old_blog_page_text_content

        new_blog_page_text_content = ExceptionTypeFrame(parent=frame2, exception_type="NEW_BLOG_CONTENT_IGNORE")
        self.pages["New Blog Page Text Content"] = new_blog_page_text_content

        old_blog_page_images = ExceptionTypeFrame(parent=frame2, exception_type="OLD_BLOG_IMAGE_IGNORE")
        self.pages["Old Blog Page Images"] = old_blog_page_images

        new_blog_page_images = ExceptionTypeFrame(parent=frame2, exception_type="NEW_BLOG_IMAGE_IGNORE")
        self.pages["New Blog Page Images"] = new_blog_page_images

        old_blog_page_links = ExceptionTypeFrame(parent=frame2, exception_type="OLD_BLOG_LINK_IGNORE")
        self.pages["Old Blog Page Links"] = old_blog_page_links

        new_blog_page_links = ExceptionTypeFrame(parent=frame2, exception_type="NEW_BLOG_LINK_IGNORE")
        self.pages["New Blog Page Links"] = new_blog_page_links

        old_forms_page = ExceptionTypeFrame(parent=frame2, exception_type="OLD_FORM_ENTRY_IGNORE")
        self.pages["Old Forms Page"] = old_forms_page

        new_forms_page = ExceptionTypeFrame(parent=frame2, exception_type="NEW_FORM_ENTRY_IGNORE")
        self.pages["New Forms Page"] = new_forms_page

        select_var.set(options[0])
        self.show_frame(options[0])

    def show_frame(self, value):
        self.pages[value].lift()

    def fetch_data(self):
        data = {}
        for key, value in self.pages.iteritems():
            data.update(self.pages[key].fetch_data())
        return data


class ExceptionTypeFrame(Frame):
    def __init__(self, parent, exception_type):
        Frame.__init__(self, master=parent)
        self.exception_type = exception_type

        self.grid(row=0, column=0, sticky=NSEW)

        self.canvas = Canvas(self, bd=0, relief=FLAT)
        self.canvas.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

        self.entry_frame = Frame(self.canvas)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.canvas, command=self.canvas.yview)
        self.canvas["yscrollcommand"] = self.scrollbar.set

        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.window = self.canvas.create_window((0, 0), window=self.entry_frame, anchor=NW)
        self.canvas.itemconfigure(self.window)
        self.entry_frame.bind("<Configure>", self.set_canvas)
        self.canvas.bind("<Configure>", self.resize_window)

        header_frame = Frame(self.entry_frame)
        header_frame.pack(side=TOP, fill=X, expand=False, padx=2)
        header_frame.columnconfigure(2, weight=3)
        header_frame.columnconfigure(4, weight=2)

        self.lbl1 = Label(header_frame, text="Tag Name", anchor=CENTER, bd=1, relief=GROOVE, width=16)
        self.lbl1.grid(row=0, column=0, sticky=NSEW)

        self.lbl2 = Label(header_frame, text="Attribute Name", anchor=CENTER, bd=1, relief=GROOVE, width=24)
        self.lbl2.grid(row=0, column=1, sticky=NSEW)

        self.lbl3 = Label(header_frame, text="Equals / Contains", anchor=CENTER, bd=1, relief=GROOVE)
        self.lbl3.grid(row=0, column=2, sticky=NSEW)

        self.lbl4 = Label(header_frame, text="Attribute Value", anchor=CENTER, bd=1, relief=GROOVE, width=25)
        self.lbl4.grid(row=0, column=3, sticky=NSEW)

        self.lbl5 = Label(header_frame, text="Inverse", anchor=CENTER, bd=1, relief=GROOVE, width=8)
        self.lbl5.grid(row=0, column=4, sticky=NSEW)

        self.lbl6 = Label(header_frame, text="Remove", anchor=CENTER, bd=1, relief=GROOVE, width=9)
        self.lbl6.grid(row=0, column=5, sticky=NSEW)

        file = open(CONFIG_FILE_PATH, 'r')
        data = json.load(file)
        file.close()

        self.tag_frames = []

        tag_frame = TagSettingFrame(parent=self.entry_frame, controller=self, tags=data[exception_type],
                                    exception_type=exception_type)
        tag_frame.pack(side=TOP, fill=BOTH, expand=True)
        self.tag_frames.append(tag_frame)

    def set_canvas(self, event):
        self.canvas["scrollregion"] = self.canvas.bbox("all")

    def resize_window(self, event):
        self.canvas.itemconfigure(self.window, width=event.width - 20)

    def fetch_data(self):
        data = {}
        for frame in self.tag_frames:
            data.update(frame.fetch_data())
        return data


class TagSettingFrame(Frame):
    def __init__(self, parent, controller, tags, exception_type):
        Frame.__init__(self, parent)
        self.controller = controller
        self.exception_type = exception_type
        self.entry_id = 0

        self.container = Frame(self)
        self.container.pack(side=TOP, fill=BOTH, expand=True)

        self.button_container = Frame(self)
        self.button_container.pack(side=TOP, fill=X, expand=False)
        self.add_button = Button(self.button_container, text="Add", command=self.add_entry)
        self.add_button.pack(side=LEFT, padx=5, pady=5)

        self.entries = []

        for tag in tags:
            self.add_entry(tag)

    def add_entry(self, tag_info=None):
        self.entry_id += 1
        entry_id = self.entry_id
        entry_container = Frame(self.container)
        entry_container.pack(side=TOP, fill=X, expand=True)
        entry_container.columnconfigure(2, weight=1)

        tag_name = StringVar()
        attr_name = StringVar()
        equal = StringVar()
        attr_value = StringVar()
        inverse = StringVar()

        if tag_info:
            tag_name.set(tag_info[0])
            attr_name.set(tag_info[1])
            attr_value.set(tag_info[2])
            equal.set(tag_info[3])
            inverse.set(tag_info[4])

        tag_name_entry = Entry(entry_container, textvariable=tag_name, bd=1, relief=GROOVE, width=18)
        tag_name_entry.grid(row=0, column=0, sticky=E + W, padx=2)

        attr_name_entry = Entry(entry_container, textvariable=attr_name, bd=1, relief=GROOVE, width=28)
        attr_name_entry.grid(row=0, column=1, sticky=E + W, padx=2)

        equal_options = ["Equals", "Contains"]
        equal_menu = OptionMenu(entry_container, equal, *equal_options)
        equal_menu.grid(row=0, column=2, sticky=E + W, padx=2)
        equal.set(equal_options[0])

        attr_value_entry = Entry(entry_container, textvariable=attr_value, bd=1, relief=GROOVE, width=28)
        attr_value_entry.grid(row=0, column=3, sticky=E + W, padx=2)

        inverse_options = ["No", "Yes"]
        inverse_menu = OptionMenu(entry_container, inverse, *inverse_options)
        inverse_menu.grid(row=0, column=4, sticky=E + W, padx=2)
        inverse.set(inverse_options[0])

        remove_btn = Button(entry_container, text="Remove", anchor=CENTER,
                            command=lambda: self.remove_entry(entry_id, entry_container), width=8)
        remove_btn.grid(row=0, column=5, sticky=E + W, padx=2)

        entry_info = [tag_name_entry, attr_name_entry, equal, attr_value_entry, inverse, entry_id]
        self.entries.append(entry_info)

    def remove_entry(self, entry_id, container):
        for i in range(len(self.entries)):
            entry_info = self.entries[i]
            if entry_info[-1] == entry_id:
                del self.entries[i]
                break
        container.destroy()
        self.button_container.pack(side=TOP)

    def fetch_data(self):
        tags = []
        exception_type = self.exception_type
        for entry_info in self.entries:
            tag_name = entry_info[0].get().lower()
            attr_name = entry_info[1].get().lower()
            equal = entry_info[2].get()
            attr_value = entry_info[3].get()
            inverse = entry_info[4].get()

            if attr_name.lower() == "class":
                attr_name = "class_"
            if attr_name.lower() == "name":
                attr_name = "name_"

            tags.append([tag_name, attr_name, attr_value, equal, inverse])
        return {exception_type: tags}


class SpecialCharacterSetting(LabelFrame):
    def __init__(self, parent, controller, text):
        LabelFrame.__init__(self, parent, text=text)

        self.canvas = Canvas(self)
        self.canvas.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

        scrollbar = Scrollbar(self.canvas, command=self.canvas.yview)
        self.canvas["yscrollcommand"] = scrollbar.set
        scrollbar.pack(side=RIGHT, fill=Y)

        self.config_frame = SpecialCharacterFrame(self.canvas)
        self.window = self.canvas.create_window((0, 0), window=self.config_frame, anchor=NW)
        self.config_frame.bind("<Configure>", self.set_canvas)
        self.canvas.bind("<Configure>", self.set_window)

        search_frame = UnicodeLookUpFrame(self)
        search_frame.pack(side=BOTTOM, fill=X, expand=False, padx=6, pady=5)

    def set_canvas(self, *args):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def set_window(self, event):
        self.canvas.itemconfigure(self.window, width=event.width - 20)

    def fetch_data(self):
        data = self.config_frame.fetch_data()
        return {"SPECIAL_CHARACTERS": data}


class SpecialCharacterFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, master=parent)

        self.ind = 0
        self.entries = []

        self.setting_frame = Frame(self)
        self.setting_frame.pack(side=TOP, fill=BOTH, expand=True)

        for pair in config.settings["SPECIAL_CHARACTERS"]:
            self.add_entry(old_char=pair[0], new_char=pair[1])

        btn_frame = Frame(self)
        btn_frame.pack(side=TOP, fill=X, expand=False)

        add_button = Button(btn_frame, command=self.add_entry, text="Add")
        add_button.pack(side=LEFT, padx=6, pady=6)

    def add_entry(self, old_char=None, new_char=None, *args):
        self.ind += 1
        entry_id = self.ind
        entry_frame = Frame(self.setting_frame)
        entry_frame.pack(side=TOP)

        old_var = StringVar()
        new_var = StringVar()

        if old_char and new_char:
            old_var.set(old_char)
            new_var.set(new_char)

        old_entry = Entry(entry_frame, textvariable=old_var, width=5)
        old_entry.pack(side=LEFT)

        lbl = Label(entry_frame, text=" => ")
        lbl.pack(side=LEFT)

        new_entry = Entry(entry_frame, textvariable=new_var, width=5)
        new_entry.pack(side=LEFT)

        remove_button = Button(entry_frame, text="Remove",
                               command=lambda: self.remove_entry(entry_id=entry_id, container=entry_frame))
        remove_button.pack(side=LEFT, padx=3, pady=3)

        self.entries.append((old_entry, new_entry, entry_id))

    def remove_entry(self, entry_id, container, *args):
        for i in range(len(self.entries)):
            entry = self.entries[i]
            if entry[2] == entry_id:
                del self.entries[i]
                break
        container.destroy()

    def fetch_data(self):
        data = []
        for pair in self.entries:
            old_char = pair[0].get()
            new_char = pair[1].get()
            data.append((old_char, new_char))
        return data
