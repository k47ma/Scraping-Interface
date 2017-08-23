# coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from Migrator_util import login
from config import *
from QA_request import get_soup
from QA_util import migration_print

# create content space pages under root_url


# create all subpages under root_url
def create_subpages(root_url, subpages, browser, progress_var=None, step=20.0):
    wait = WebDriverWait(browser, 20)
    browser.get(root_url)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    # log into the page if the site needs login
    if browser.title == "Login":
        login(browser, wait)

    page_step = step / len(subpages)

    # create content space page at root_url
    for page in subpages:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            return

        browser.get(root_url)
        try:
            page_option = browser.find_element_by_xpath("//li[@class='optionAddPage']")
            page_option.click()
        except NoSuchElementException:
            migration_print("Unable to create subpage for " + root_url)
            if progress_var:
                progress_var.set(progress_var.get() + page_step)
            continue

        content_space_page = browser.find_element_by_xpath(
            '//li[@class="optionAddPage"]//ul//li/a[text()="Content Space Page"]')
        content_space_page.click()

        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            return

        # use different names for horizontal and vertical templates
        try:
            page_title_entry = browser.find_element_by_name("ctl00$ContentPlaceHolder1$ctl06$txtTitle")
        except NoSuchElementException:
            page_title_entry = browser.find_element_by_name("ctl00$ContentPlaceHolder1$ctl01$txtTitle")
        page_title_entry.send_keys(page[0])

        generate_title = browser.find_element_by_xpath("//img[@title='Generate Name']")
        generate_title.click()

        try:
            page_name_entry = browser.find_element_by_name("ctl00$ContentPlaceHolder1$ctl06$txtCanonicalName")
        except NoSuchElementException:
            page_name_entry = browser.find_element_by_name("ctl00$ContentPlaceHolder1$ctl01$txtCanonicalName")
        page_name_entry.clear()
        page_name_entry.send_keys(page[1])

        try:
            create_page = browser.find_element_by_name("ctl00$ContentPlaceHolder1$ctl06$btnSubmit")
        except NoSuchElementException:
            create_page = browser.find_element_by_name("ctl00$ContentPlaceHolder1$ctl01$btnSubmit")
        create_page.click()

        migration_print(page[0] + " (" + page[1] + ") created!")

        if progress_var:
            progress_var.set(progress_var.get() + page_step)


# get subpages from navigation menu and parse it into the formatted list
def get_subpages(old_url):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return []

    old_soup = get_soup(old_url)
    nav_menu = old_soup.find('ul', class_="primary-navigation")
    try:
        drop_downs = nav_menu.find_all('ul')
    except AttributeError:
        return []

    parsed_subpages = []
    for drop_down in drop_downs:
        subpages = drop_down.find_all('a')
        if not subpages:
            continue
        else:
            url_list = subpages[0]['href'].split('/')
            root_url = '/' + url_list[1]
        parsed_subpage = []
        for subpage in subpages:
            name = subpage.get_text()
            rel_url = subpage['href'].split('/')[-1]
            parsed_subpage.append((name, rel_url))
        parsed_subpages.append((root_url, parsed_subpage))

    return parsed_subpages


# migrate all the subpages according to nav menu
def migrate_subpages(old_url, new_url, progress_var=None, step=100.0):
    old_url = old_url.strip()
    new_url = new_url.strip()

    # remove the "/" at the end of the url
    if old_url[-1] == '/':
        old_url = old_url[:-1]
    if new_url[-1] == '/':
        new_url = new_url[:-1]

    # add "http://" before url
    if not old_url.startswith("http"):
        old_url = "http://" + old_url
    if not new_url.startswith("http"):
        new_url = "http://" + new_url

    # print out the information for old and new sites
    migration_print("-----------------------------------------------------")
    migration_print("Old URL: " + old_url)
    migration_print("New URL: " + new_url)
    migration_print("-----------------------------------------------------")

    browser = webdriver.Chrome(executable_path=settings["EXECUTABLE_PATH"])
    wait = WebDriverWait(browser, 20)
    browser.maximize_window()

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        migration_print("-----------------------------------------------------\n")
        return

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.01)

    if old_url.endswith('/'):
        old_url = old_url[:-1]
    if new_url.endswith('/'):
        new_url = new_url[:-1]

    parsed_subpages = get_subpages(old_url)
    browser.get(new_url)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        migration_print("-----------------------------------------------------\n")
        return

    # log into the page if the site needs login
    if browser.title == "Login":
        login(browser, wait)

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.02)

    step *= 0.97

    # avoid divided by zero error
    if not parsed_subpages:
        migration_print("Unable to fetch subpages from navigation menu of " + old_url)
        return

    root_step = step / len(parsed_subpages)

    for page in parsed_subpages:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            break

        create_subpages(new_url + page[0], page[1], browser, progress_var=progress_var, step=root_step)

    migration_print("-----------------------------------------------------\n")
    browser.quit()
