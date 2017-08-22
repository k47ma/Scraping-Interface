# coding=utf-8
import csv
from ThreadPool import ThreadPool
from QA_request import get_soup, get_sites, get_blog_site
from QA_error import record_error
from QA_compare_normal import compare_meta_soup, compare_content_soup, compare_image_soup, compare_link_soup
from QA_compare_homepage import compare_homepage
from QA_compare_blog import compare_blog
from QA_compare_form import compare_form_soup
from QA_util import create_path, entry_print
from config import *


# module for creating and running threads


# compare sites using threading
def compare_site_thread(old_url, new_url, progress_var=None, step=100.0, thread_pool_csv=None):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    # checking multiple sites mode
    if thread_pool_csv:
        thread_pool = thread_pool_csv
    else:
        thread_pool = ThreadPool(settings["THREADPOOL_SIZE"])
    create_path()
    ind = 0

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

    setup_step = step * 0.01
    if progress_var:
        progress_var.set(progress_var.get() + setup_step)

    # check if the new site needs login
    new_test = get_soup(new_url)
    if new_test:
        title = new_test.find("title")
        if title and title.get_text().strip() == "Login":
            entry_print("New site needs login. Please use login mode to check this site!\n", True)
            return -1

    setup_step = step * 0.01
    if progress_var:
        progress_var.set(progress_var.get() + setup_step)

    # get the subpages of old and new sites
    sites = get_sites(old_url)
    old_blog = get_blog_site(old_url)
    new_blog = get_blog_site(new_url)

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        thread_pool.destroy()
        return

    blog_exists = False
    if old_blog and new_blog:
        blog_exists = True

    # if urls for subpages are not found
    if sites is None:
        record_error(new_url, "sites")
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False

    # if blog page is not found
    if old_blog is not None and new_blog is None:
        record_error(new_url, "blog")
    elif old_blog is None and new_blog is not None:
        record_error(old_url, "blog")

    setup_step = step * 0.02
    if progress_var:
        progress_var.set(progress_var.get() + setup_step)

    # calculate the step for each page
    step *= 0.96
    if blog_exists:
        page_step = step / 2 / (len(sites) + 1)
    else:
        page_step = step / (len(sites) + 1)

    # check the homepage
    thread_pool.add_task(compare_homepage, old_url=old_url, new_url=new_url, progress_var=progress_var,
                         step=page_step)

    # check all the sites in sitemap
    for site in sites:
        ind += 1
        if site.startswith("/home") or site.startswith("/main"):
            continue

        old_link = old_url + site
        new_link = new_url + site

        thread_pool.add_task(compare_page, old_url=old_link, new_url=new_link, progress_var=progress_var,
                             step=page_step)

    # check all the blog pages
    if blog_exists:
        old_blog_soup = get_soup(old_blog)
        new_blog_soup = get_soup(new_blog)
        compare_blog(old_blog_soup, new_blog_soup, old_blog, new_blog, progress_var=progress_var,
                     step=step / 2)

    # single site mode
    if not thread_pool_csv:
        thread_pool.wait_completion()
        thread_pool.destroy()

    entry_print("-----------------------------------------------------\n")

    return True


# compare all the sites in file
def compare_site_thread_csv(file, progress_var=None, step=100.0):
    if status["INTERFACE_MODE"]:
        thread_pool_csv = ThreadPool(settings["THREADPOOL_SIZE"])
    else:
        thread_pool_csv = ThreadPool(20)

    f = open(file, 'r')

    # calculate the step for each site
    row_count = sum(1 for row in f)
    site_step = step / row_count
    f.close()

    f = open(file, 'r')
    rows = csv.reader(f)

    for row in rows:
        compare_site_thread(row[0], row[1], progress_var=progress_var, step=site_step, thread_pool_csv=thread_pool_csv)
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            f.close()
            return
    f.close()

    thread_pool_csv.wait_completion()
    thread_pool_csv.destroy()


# compare everything for normal pages
def compare_page(old_url, new_url, browser=None, progress_var=None, step=1.0):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    # deal with urls that exceeds 50 characters
    new_list = new_url.split("/")
    if new_list[-1].find("televox.west.com") == -1 and len(new_list[-1]) > 50:
        new_list[-1] = new_list[-1][:50]
    new_url = "/".join(new_list)

    old_soup = get_soup(old_url)
    new_soup = get_soup(new_url, browser=browser)
    result = open("result\\site_result.txt", 'a')

    if old_soup is None:
        record_error(old_url, "soup")
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False
    if new_soup is None:
        record_error(new_url, "soup")
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False

    meta_pass = compare_meta_soup(old_soup, new_soup, old_url, new_url)

    if meta_pass == -1:
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False

    form_pass = compare_form_soup(old_soup, new_soup, old_url, new_url)
    content_pass = compare_content_soup(old_soup, new_soup, old_url, new_url)
    image_pass = compare_image_soup(old_soup, new_soup, old_url, new_url)
    link_pass = compare_link_soup(old_soup, new_soup, old_url, new_url, browser=browser)
    page_pass = meta_pass and form_pass and content_pass and image_pass and link_pass

    if page_pass:
        print(new_url + " PASSED!")
        result.write(new_url + " PASSED!\n")
        result.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return True
    else:
        print(new_url + " FAILED! (see detail files for more information)")
        result.write(new_url + " FAILED! (see detail files for more information)\n")
        result.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False
