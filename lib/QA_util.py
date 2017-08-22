# coding=utf-8
import os
import string
from config import *
from ThreadSafeText import *

# module for helper functions


# stripe the url and get the domain name
def get_domain(url):
    if url[:7] == "http://":
        url = url[7:]
    elif url[:8] == "https://":
        url = url[8:]
    url_split = url.split(".")
    if url_split[0] == "www":
        domain = url_split[1]
    else:
        domain = url_split[0]
    return domain


# remove special characters in text
def replace_special(text):
    text = text.decode('utf-8', errors="ignore")

    for (old, new) in settings["SPECIAL_CHARACTERS"]:
        text = text.replace(old, new).strip()

    printable = set(string.printable)
    text = "".join([i for i in text if i in printable]).strip()
    text = " ".join(text.splitlines())

    while text.find("  ") != -1:
        text = text.replace("  ", " ")

    return text


# determine whether address is in correct form
def check_format(address):
    address = address.lower()
    if address.find("suite") != -1 and address.find(",") == -1:
        return False
    if (address.find(" st") != -1 and address[address.find(" st")+3:].isspace()) \
            or (address.find(" ave") != -1 and address.find("avenue") == -1) or address.find(" blvd") != -1 \
            or (address.find(" hwy") != -1 and address[address.find(" hwy")+4:].isspace()) or address.find(" rd") != -1 \
            or address.find(" pkwy") != -1:
        if address.find(".,") == -1 or address.find(" .,") != -1:
            return False
    return True


# clear all the history records
def clear_all():
    create_path()
    file1 = open("result\\address_detail.txt", 'w')
    file2 = open("result\\meta_detail.txt", 'w')
    file3 = open("result\\content_detail.txt", 'w')
    file4 = open("result\\site_result.txt", 'w')
    file5 = open("result\\site_detail.txt", 'w')
    file6 = open("result\\error.txt", 'w')
    file7 = open("result\\blog_detail.txt", 'w')
    file8 = open("result\\homepage_detail.txt", 'w')
    file9 = open("result\\form_detail.txt", 'w')
    file10 = open("result\\QA_result.txt", 'w')
    file1.close()
    file2.close()
    file3.close()
    file4.close()
    file5.close()
    file6.close()
    file7.close()
    file8.close()
    file9.close()
    file10.close()


# create the result folder
def create_path():
    if not os.path.exists("result"):
        os.makedirs("result")
    return


# print content to interface dialog
def entry_print(content, add_to_text=False):
    print content

    summary = open("result\\QA_result.txt", 'a')
    summary.write(content + "\n")
    summary.close()

    textarea = status["CURRENT_ENTRY"]
    if textarea and add_to_text:
        textarea.insert(END, content + "\n")
        textarea.see(END)
