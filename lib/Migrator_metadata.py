# coding=utf-8
import re
from urlparse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Migrator_util import login, ask_continue
from config import *
from QA_request import get_soup, get_blog_site, get_sites
from QA_get import get_meta_soup
from QA_util import entry_print

# module for migrating metadata


# set metadata for new page
def set_meta(old_url, new_url, browser):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    wait = WebDriverWait(browser, 20)
    old_soup = get_soup(old_url)
    old_meta = get_meta_soup(old_soup, old_url)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    if new_url.endswith('/'):
        new_url = new_url[:-1]

    # truncate url if name exceeds 50 characters
    new_path = urlparse(new_url).path
    new_path_list = new_path.split('/')
    if len(new_path_list[-1]) > 50:
        new_path_list[-1] = new_path_list[-1][:50]
        new_path_dup = "/".join(new_path_list)
        new_url_dup = new_url.replace(new_path, new_path_dup)
        browser.get(new_url_dup)
    else:
        browser.get(new_url)

    if browser.title == "Login":
        login(browser, wait)

    new_soup = BeautifulSoup(browser.page_source, "html.parser")
    login_status = new_soup.find('a', id="ctl00_lnkGateway").get_text()
    if login_status == "Login":
        login_button = browser.find_element_by_id("ctl00_lnkGateway")
        login_button.click()
        wait.until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtUsername")))
        login(browser, wait)

    page_options = browser.find_element_by_xpath('//li[@class="optionPageOptions"]')
    page_options.click()

    metadata_option = browser.find_element_by_xpath('//span[@class="AB_icn AB_icn-metadata"]').find_element_by_xpath(
        '..')
    url = metadata_option.get_attribute('href')
    rel_url = re.search("/cms/.*Metadata", url).group(0)
    new_hostname = urlparse(new_url).hostname
    target_url = "http://" + new_hostname + rel_url

    browser.get(target_url)

    enable_custom_checkbox = browser.find_elements_by_xpath('//input[@type="checkbox"]')[0]
    if not enable_custom_checkbox.is_selected():
        enable_custom_checkbox.click()

    # migrate title
    title = old_meta["title"]
    title_entry = browser.find_elements_by_xpath('//input[@type="text"]')[6]
    title_entry.clear()
    try:
        title_entry.send_keys(title)
    except UnicodeDecodeError:
        entry_print("Unable to migrate title for " + new_url, True)
        entry_print("Title: " + old_meta["title"], True)
        entry_print("Description: " + old_meta["description"], True)
        entry_print("Keywords: " + old_meta["keywords"], True)
        entry_print("-----------------------------------------------------------", True)
        ask_continue()
        return

    # migrate description
    description = old_meta["description"]
    if description != "none" and not description.startswith("Learn more about"):
        description_entry = browser.find_elements_by_xpath('//input[@type="text"]')[13]
        description_entry.clear()
        try:
            description_entry.send_keys(description)
        except UnicodeDecodeError:
            entry_print("Unable to migrate description for " + new_url, True)
            entry_print("Title: " + old_meta["title"], True)
            entry_print("Description: " + old_meta["description"], True)
            entry_print("Keywords: " + old_meta["keywords"], True)
            entry_print("-----------------------------------------------------------")
            ask_continue()
            return

    # migrate keywords
    keywords = old_meta["keywords"]
    if keywords != "none":
        keywords_entry = browser.find_elements_by_xpath('//input[@type="text"]')[14]
        keywords_entry.clear()
        try:
            keywords_entry.send_keys(keywords)
        except UnicodeDecodeError:
            entry_print("Unable to migrate keywords for " + new_url, True)
            entry_print("Title: " + old_meta["title"], True)
            entry_print("Description: " + old_meta["description"], True)
            entry_print("Keywords: " + old_meta["keywords"], True)
            entry_print("-----------------------------------------------------------", True)
            ask_continue()
            return

    submit_button = browser.find_element_by_xpath('//input[@type="submit"]')
    submit_button.click()

    new_path = urlparse(new_url).path
    if not new_path:
        new_path = "/"
    entry_print(new_path + " metadata migrated!", True)


# migrate metadata for new site
def migrate_meta(old_url, new_url, progress_var=None, step=100.0):
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
    entry_print("-----------------------------------------------------", True)
    entry_print("Old URL: " + old_url, True)
    entry_print("New URL: " + new_url, True)
    entry_print("-----------------------------------------------------", True)

    browser = webdriver.Chrome(executable_path=settings["EXECUTABLE_PATH"])
    browser.maximize_window()

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        entry_print("-----------------------------------------------------\n", True)
        return

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.01)

    sites = get_sites(old_url)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        entry_print("-----------------------------------------------------\n", True)
        return

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.02)

    if not sites:
        entry_print("Unable to fetch subpage URLs form site map of " + old_url, True)

    # find blog pages
    old_blog_page = get_blog_site(old_url)
    new_blog_page = get_blog_site(new_url)
    blog_exists = True

    if not old_blog_page or not new_blog_page:
        blog_exists = False

    # calculate the step for each subpage
    step *= 0.97
    if blog_exists:
        page_step = step / 2 / (len(sites) + 1)
    else:
        page_step = step / (len(sites) + 1)

    # migrate metadata for homepage
    set_meta(old_url, new_url, browser)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        entry_print("-----------------------------------------------------\n", True)
        return

    if progress_var:
        progress_var.set(progress_var.get() + page_step)

    # migrate all non-blog pages
    for site in sites:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            browser.quit()
            entry_print("-----------------------------------------------------\n", True)
            return

        old_link = old_url + site
        new_link = new_url + site
        try:
            set_meta(old_link, new_link, browser)
        except NoSuchElementException:
            entry_print("Missing Page: " + new_link, True)
        if progress_var:
            progress_var.set(progress_var.get() + page_step)

    if not blog_exists:
        browser.quit()
        entry_print("-----------------------------------------------------------", True)
        return

    step /= 2

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        entry_print("-----------------------------------------------------\n", True)
        return

    old_blog_soup = get_soup(old_blog_page)
    new_blog_soup = get_soup(new_blog_page, browser)

    old_blogs = old_blog_soup.find_all(['h5', 'h3'])
    new_blogs = new_blog_soup.find_all('a', class_="title")

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        entry_print("-----------------------------------------------------\n", True)
        return

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.02)

    step *= 0.98

    # record blog posts as title, url pairs in dictionary
    old_list = []
    parsed_old_blogs = {}
    ind = 1
    for blog in old_blogs:
        title = blog.get_text()
        if title == "Categories":
            old_blogs.remove(blog)
            continue

        try:
            link = blog.a.get('href')
        except AttributeError:
            entry_print("Unable to find blog metadata for " + title, True)

        if title in parsed_old_blogs:
            parsed_old_blogs[title + str(ind)] = link
            old_list.append((title + str(ind), link))
            ind += 1
        else:
            parsed_old_blogs[title] = link
            old_list.append((title, link))

    new_list = []
    parsed_new_blogs = {}
    ind = 1
    for blog in new_blogs:
        title = blog.get_text()
        link = new_url + blog.get('href')
        if title in parsed_new_blogs:
            parsed_new_blogs[title + str(ind)] = link
            new_list.append((title + str(ind), link))
            ind += 1
        else:
            parsed_new_blogs[title] = link
            new_list.append((title, link))

    if not old_list or not new_list:
        browser.quit()
        return

    blog_step = step / (len(old_list) + 1)

    # migrate metadata for blog index page
    set_meta(old_blog_page, new_blog_page, browser)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        browser.quit()
        entry_print("-----------------------------------------------------\n", True)
        return

    if progress_var:
        progress_var.set(progress_var.get() + blog_step)

    # migrate metadata for blog posts
    for ind in range(len(old_list)):
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            browser.quit()
            entry_print("-----------------------------------------------------\n", True)
            return

        if old_list[ind][0] == new_list[ind][0]:
            set_meta(old_list[ind][1], new_list[ind][1], browser)
        else:
            try:
                set_meta(parsed_old_blogs[old_list[ind][0]], parsed_new_blogs[old_list[ind][0]], browser)
            except KeyError:
                entry_print("Cannot migrate metadata for blog page " + new_list[ind][1], True)
                continue
        if progress_var:
            progress_var.set(progress_var.get() + blog_step)

    browser.quit()
    entry_print("-----------------------------------------------------\n", True)
