# coding=utf-8
import csv
from selenium import webdriver
from config import *
from QA_compare_thread import compare_page
from QA_compare_homepage import compare_homepage
from QA_compare_blog import compare_blog
from QA_error import record_error
from QA_request import get_soup, get_sites, get_blog_site, get_soup_selenium
from QA_util import create_path, entry_print


# module for comparing sites with Selenium


# use Selenium to compare two sites
def compare_site_selenium(old_url, new_url, progress_var=None, step=100.0):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        entry_print("-----------------------------------------------------\n")
        return

    create_path()
    new_browser = webdriver.Chrome(executable_path=settings["EXECUTABLE_PATH"])
    new_browser.maximize_window()
    site_pass = True
    blog_pass = True
    ind = 0

    old_url = old_url.strip()
    new_url = new_url.strip()

    # remove the "/" at the end of url
    if old_url.endswith('/'):
        old_url = old_url[:-1]
    if new_url.endswith('/'):
        new_url = new_url[:-1]

    # print out the information for old and new sites
    entry_print("-----------------------------------------------------", True)
    entry_print("Old URL: " + old_url, True)
    entry_print("New URL: " + new_url, True)
    entry_print("-----------------------------------------------------", True)

    setup_step = step * 0.01
    if progress_var:
        progress_var.set(progress_var.get() + setup_step)

    # get the domain name of old url and derive the new url
    sites = get_sites(old_url)
    old_blog = get_blog_site(old_url)
    new_blog = get_blog_site(new_url)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        new_browser.quit()
        entry_print("-----------------------------------------------------\n")
        return

    blog_exists = False
    if old_blog and new_blog:
        blog_exists = True

    # if subpages are not found
    if sites is None:
        record_error(new_url, "sites")
        return False

    # if blog page is not found
    if old_blog is not None and new_blog is None:
        record_error(new_url, "blog")
    elif old_blog is None and new_blog is not None:
        record_error(old_url, "blog")

    setup_step = step * 0.02
    step *= 0.97
    if progress_var:
        progress_var.set(progress_var.get() + setup_step)

    if blog_exists:
        page_step = step / 2 / (len(sites) + 1)
    else:
        page_step = step / (len(sites) + 1)

    # check homepage
    homepage_pass = compare_homepage(old_url, new_url, browser=new_browser, progress_var=progress_var, step=page_step)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        new_browser.quit()
        entry_print("-----------------------------------------------------\n")
        return

    if homepage_pass == -1:
        return -1

    # check all the sites in sitemap
    for site in sites:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            new_browser.quit()
            entry_print("-----------------------------------------------------\n")
            return

        ind += 1
        if site.startswith("/home") or site.startswith("/main"):
            continue

        old_link = old_url + site
        new_link = new_url + site

        page_pass = compare_page(old_link, new_link, browser=new_browser, progress_var=progress_var, step=page_step)

        if not page_pass:
            site_pass = False

    # check all the blog entries
    if blog_exists:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            new_browser.quit()
            entry_print("-----------------------------------------------------\n")
            return

        old_blog_soup = get_soup(old_blog)
        new_blog_soup = get_soup_selenium(new_blog, new_browser)
        blog_pass = compare_blog(old_blog_soup, new_blog_soup, old_blog, new_blog, browser=new_browser,
                                 progress_var=progress_var, step=step / 2)

    entry_print("-----------------------------------------------------\n")
    new_browser.quit()

    return site_pass and homepage_pass and blog_pass


# use Selenium to compare multiple sites in csv file
def compare_site_selenium_csv(file, progress_var=None, step=100.0):
    f = open(file, 'r')

    # calculate the step for each site
    row_count = sum(1 for row in f)
    site_step = step / row_count
    f.close()

    f = open(file, 'r')
    rows = csv.reader(f)
    for row in rows:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            f.close()
            return
        compare_site_selenium(row[0], row[1], progress_var=progress_var, step=site_step)
    f.close()
