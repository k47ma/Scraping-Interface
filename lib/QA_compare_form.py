# coding=utf-8
import re
from config import settings
from QA_util import replace_special, entry_print
from QA_error import record_error

# module for comparing the information for form pages


# compare the form pages
def compare_form_soup(old_soup, new_soup, old_url, new_url):
    detail = open("result\\form_detail.txt", 'a')
    require_pass = True
    title_pass = True
    entry_pass = True
    auth_pass = True
    old_container = old_soup.find('div', class_="form-container")
    new_container = new_soup.find('div', class_="secureform")

    if not old_container and not new_container:
        detail.close()
        return True
    elif not old_container and new_container:
        record_error(old_url, "form container")
        detail.close()
        return False
    elif old_container and not new_container:
        record_error(new_url, "form container")
        detail.close()
        return False

    # check the "required field" text in new form
    if not new_container.find(text=re.compile("required field")):
        entry_print("***********************************************")
        entry_print("FORM MISSING '* REQUIRED FIELD' TITLE!")
        entry_print("New URL: " + new_url)
        entry_print("***********************************************")
        detail.write("FORM MISSING '* REQUIRED FIELD' TITLE!\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("-----------------------------------------------\n")
        require_pass = False

        # find all the entry names and choices from old page
    if old_container:
        for (name, kwargs) in settings["OLD_FORM_ENTRY_IGNORE"]:
            for s in old_container.find_all(name, **kwargs):
                s.extract()
    old_entries = [replace_special(text) for text in old_container.stripped_strings]

    # find all the entry names and choices from new page
    if new_container:
        for (name, kwargs) in settings["NEW_FORM_ENTRY_IGNORE"]:
            for s in new_container.find_all(name, **kwargs):
                s.extract()
    new_entries = [replace_special(text) for text in new_container.stripped_strings]

    # compare entry names
    if len(old_entries) != len(new_entries):
        entry_print("***********************************************")
        entry_print("NUMBER OF FORM ENTRIES DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old entries: " + str(len(old_entries)))
        entry_print("Number of new entries: " + str(len(new_entries)))
        entry_print("Old entries: " + str(old_entries))
        entry_print("New entries: " + str(new_entries))
        detail.write("NUMBER OF FORM ENTRIES DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old entries: " + str(len(old_entries)) + "\n")
        detail.write("Number of new entries: " + str(len(new_entries)) + "\n")
        detail.write("Old entries: " + str(old_entries) + "\n")
        detail.write("New entries: " + str(new_entries) + "\n")
        entry_pass = False

        # try to track down the issue
        for ind in range(min(len(old_entries), len(new_entries))):
            if old_entries[ind] != new_entries[ind] and old_entries[ind].upper() != new_entries[ind].upper():
                entry_print("FIRST DIFFERENCE:")
                entry_print("Old entry name: " + old_entries[ind])
                entry_print("New entry name: " + new_entries[ind])
                detail.write("FIRST DIFFERENCE:\n")
                detail.write("Old entry name: " + old_entries[ind] + "\n")
                detail.write("New entry name: " + new_entries[ind] + "\n")
                break
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
    else:
        # compare each entry
        count = 0
        old_diff = []
        new_diff = []
        new_pass = True

        for ind in range(len(old_entries)):
            old_entry = old_entries[ind]
            new_entry = new_entries[ind]
            if old_entry != new_entry and old_entry.upper() != new_entry.upper():
                old_diff.append(old_entry)
                new_diff.append(new_entry)
        old_diff_dup = [i.upper() for i in old_diff]
        new_diff_dup = [i.upper() for i in new_diff]
        old_diff_dup.sort()
        new_diff_dup.sort()

        for old_entry, new_entry in zip(old_diff_dup, new_diff_dup):
            if old_entry != new_entry:
                new_pass = False
                break

        if not new_pass:
            for old_entry, new_entry in zip(old_diff, new_diff):
                count += 1
                if entry_pass:
                    entry_print("***********************************************")
                    entry_print("FORM ENTRIES DO NOT MATCH!")
                    entry_print("Old URL: " + old_url)
                    entry_print("New URL: " + new_url)
                    detail.write("FORM ENTRIES DO NOT MATCH!\n")
                    detail.write("Old URL: " + old_url + "\n")
                    detail.write("New URL: " + new_url + "\n")
                    entry_pass = False
                entry_print("Old entry name" + str(count) + ": " + old_entry)
                entry_print("New entry name" + str(count) + ": " + new_entry)
                detail.write("Old entry name" + str(count) + ": " + old_entry + "\n")
                detail.write("New entry name" + str(count) + ": " + new_entry + "\n")
            entry_print("***********************************************")
            detail.write("-----------------------------------------------\n")

    detail.close()
    return require_pass and title_pass and entry_pass and auth_pass
