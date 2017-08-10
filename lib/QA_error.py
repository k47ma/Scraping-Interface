# coding=utf-8
from QA_util import entry_print

# module for recording errors


# print and record the record with type
def record_error(url, err_type):
    entry_print("***********************************************")
    entry_print("ERROR!")
    entry_print("Cannot find the " + err_type + " for " + url)
    entry_print("***********************************************")
    file = open("result\\error.txt", "a")
    file.write("ERROR!\n")
    file.write("Cannot find the " + err_type + " for " + url + "\n")
    file.write("***********************************************\n")
    file.close()


class CredentialError(Exception):
    def __init__(self):
        Exception.__init__(self)
