# coding=utf-8
import re
import sys
import tkMessageBox

# module for helper functions


# translate the tag from json format into config format
def parse_tag(tag):
    tag_name = tag[0].strip()
    attr_name = tag[1].strip()
    attr_value = tag[2].strip()
    equal = tag[3]
    inverse_select = tag[4]

    if not (tag_name or attr_name or attr_value):
        return None

    if not attr_name:
        attr = {}
    elif inverse_select == "No":
        if equal == "Equals":
            # select tags with attribute equal to the value
            attr = {attr_name: re.compile("^(" + attr_value + ")$")}
        else:
            # select tags with attribute containing the value
            attr = {attr_name: re.compile(attr_value)}
    else:
        if equal == "Equals":
            # select tags with attribute not equal to the value
            attr = {attr_name: re.compile("^(?!" + attr_value + ")$")}
        else:
            # select tags with attribute not containing the value
            attr = {attr_name: re.compile("^((?!" + attr_value + ").)*$")}

    parsed_tag = (tag_name, attr)
    return parsed_tag


def ask_quit():
    if tkMessageBox.askyesno("Quit", "Do you really wish to quit?"):
        sys.exit()
