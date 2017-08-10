# coding=utf-8
import os
import json
import config
import default_config
from Interface_util import parse_tag

# module for loading and saving configurations


CONFIG_FILE_PATH = "config\\private_config.json"


# load configuration from file
def load_config():
    if not os.path.exists("config"):
        os.makedirs("config")

    # try to open the configuration file
    try:
        add_on = open(CONFIG_FILE_PATH, 'r')
    except IOError:
        add_on = open(CONFIG_FILE_PATH, 'w')
        add_on.write("{}")
        add_on.close()
        add_on = open(CONFIG_FILE_PATH, 'r')

    # try to load the json object from file
    try:
        data = json.load(add_on)
    except ValueError:
        data = {}
    add_on.close()

    # add the exist value to config.py
    for key, value in config.settings.iteritems():
        if data.get(key) is None:
            # if the category name is not found in private settings
            if key == "USER_NAME" or key == "PASSWORD":
                data[key] = ""
                config.settings[key] = ""
            elif key == "EXECUTABLE_PATH":
                data[key] = ""
            elif key == "THREADPOOL_SIZE":
                data[key] = 5
            else:
                data[key] = []
        elif key == "USER_NAME" or key == "PASSWORD" or key == "THREADPOOL_SIZE":
            config.settings[key] = data[key]
        elif key == "EXECUTABLE_PATH":
            if data[key] != "":
                config.settings[key] = data[key]
            else:
                data[key] = config.settings[key]
        elif key == "SPECIAL_CHARACTERS":
            config.settings[key] = default_config.settings[key]
            config.settings[key] += [(pair[0], pair[1]) for pair in data[key]
                                     if pair[0] and (pair[0], pair[1]) not in config.settings[key]]
        else:
            parsed_tags = [parse_tag(tag) for tag in data[key]]
            config.settings[key] += parsed_tags

    add_on = open(CONFIG_FILE_PATH, "w")
    json.dump(data, add_on)
    add_on.close()


# save all the settings to config file
def save_config(data):
    target = open(CONFIG_FILE_PATH, 'r')
    old_data = json.load(target)
    target.close()

    for key, value in data.iteritems():
        # store the information to config
        if key == "USER_NAME" or key == "PASSWORD" or key == "EXECUTABLE_PATH":
            config.settings[key] = data[key].strip()
            old_data[key] = data[key].strip()
        elif key == "THREADPOOL_SIZE":
            config.settings[key] = data[key]
            old_data[key] = data[key]
        else:
            addon_list = []
            if key == "SPECIAL_CHARACTERS":
                addon_list = [[new_pair[0], new_pair[1]] for new_pair in data[key]]
                old_data[key] = addon_list
                config.settings[key] = data[key]
            else:
                for tag in data[key]:
                    parsed_tag = parse_tag(tag)
                    if parsed_tag is None:
                        continue
                    addon_list.append(parsed_tag)
                config.settings[key] = default_config.settings[key] + addon_list

                # update old_data
                old_data[key] = data[key]

    target = open(CONFIG_FILE_PATH, 'w')
    json.dump(old_data, target)
    target.close()
