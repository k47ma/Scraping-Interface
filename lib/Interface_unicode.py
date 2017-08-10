# coding=utf-8
import requests
import threading
import unicodedata
from bs4 import BeautifulSoup
from tkinter import *

# tool for looking up unicode


# look up the given character in unicode list
def lookup(value, type):
    hex_code = ""
    dec_code = ""
    # search unicode by hex or dec code
    if type == "hex" or type == "dec":
        # convert decimal number to hex code
        try:
            if type == "dec":
                dec_code = value
                hex_code = hex(int(value))[2:]
            else:
                dec_code = str(int(value, 16))
                hex_code = value
        except ValueError:
            return None
        except OverflowError:
            return None
    elif type == "name":
        # search unicode by name
        value = value.replace(" ", "+")
        search_url = "http://www.fileformat.info/info/unicode/char/search.htm?q=" + value.lower() + "&preview=entity"
        source_code = requests.get(search_url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "html.parser")

        result_table = soup.find('table', class_="table")
        result = result_table.find('td')

        if not result:
            return None

        hex_code = result.find('a')["href"].split("/")[0]
        dec_code = str(int(hex_code, 16))
    try:
        uni_char = unichr(int(dec_code))
        name = unicodedata.name(uni_char)
    except ValueError:
        return -1
    except OverflowError:
        return None

    return {"Hex": hex_code, "Dec": dec_code, "Name": name, "Char": uni_char}


class UnicodeLookUpFrame(LabelFrame):
    def __init__(self, parent):
        LabelFrame.__init__(self, parent)

        self["text"] = "Unicode Character Lookup Tool"

        search_frame = Frame(self)
        search_frame.pack(side=TOP, fill=BOTH, expand=True, padx=6, pady=5)

        self.entry_var = StringVar()

        self.entry = Entry(search_frame, textvariable=self.entry_var)
        self.entry.pack(side=LEFT)
        self.entry.bind("<Key-Return>", self.start_search)

        btn = Button(search_frame, text="Preview", command=self.start_search)
        btn.pack(side=LEFT, padx=5, pady=5)

        lbl2 = Label(search_frame, text="Search by:")
        lbl2.pack(side=LEFT)

        self.type_var = StringVar()

        type_hex = Radiobutton(search_frame, text="Hex Code", variable=self.type_var, value="hex")
        type_hex.pack(side=LEFT)

        type_dec = Radiobutton(search_frame, text="Decimal Code", variable=self.type_var, value="dec")
        type_dec.pack(side=LEFT)

        type_name = Radiobutton(search_frame, text="Character Name", variable=self.type_var, value="name")
        type_name.pack(side=LEFT)

        self.type_var.set("hex")

        result_frame = Frame(self)
        result_frame.pack(side=BOTTOM, fill=X, expand=False, padx=6, pady=(0, 5))

        self.result = StringVar()

        self.target = Entry(result_frame, font=12, relief=FLAT, state=DISABLED, textvariable=self.result, disabledforeground="black")
        self.target.pack(side=LEFT, fill=X, expand=True)

    def start_search(self, *args):
        thread = SearchThread(type=self.type_var.get(), value=self.entry.get(), target=self.target, var=self.result)
        thread.start()


class SearchThread(threading.Thread):
    def __init__(self, type, value, target, var):
        threading.Thread.__init__(self)
        self.type = type
        self.value = value
        self.target = target
        self.var = var

    def run(self):
        self.target["state"] = "normal"
        if not self.value:
            self.target["disabledforeground"] = "red"
            self.var.set("^ Please input a value. ^")
            self.target["state"] = "disabled"
            return

        self.target["disabledforeground"] = "black"
        self.var.set("Searching...")
        result = lookup(self.value, self.type)
        if result is None:
            self.var.set("Cannot find the unicode with " + self.type + " \"" + self.value + "\". Please check your input.")
            self.target["state"] = "disabled"
            return
        elif result == -1:
            self.var.set("Cannot display this unicode.")
            self.target["state"] = "disabled"
            return

        self.var.set(result["Name"].lower() + ": " + result["Char"] + " | Hex: " + result["Hex"] + " | Dec: " + result["Dec"])
        self.target["state"] = "disabled"
