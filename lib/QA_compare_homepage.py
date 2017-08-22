# coding=utf-8
from QA_error import record_error, CredentialError
from QA_compare_normal import compare_meta_soup, compare_address_soup
from QA_check import check_homepage_image, check_homepage_link
from QA_get import get_homepage_content
from QA_request import get_soup
from QA_util import replace_special, entry_print
from config import settings

# module for comparing information for homepages


# compare the information between old homepage and new homepage
def compare_homepage(old_url, new_url, browser=None, progress_var=None, step=1.0):
    result = open("result\\site_result.txt", 'a')

    old_soup = get_soup(old_url)
    if not browser:
        new_soup = get_soup(new_url)
    else:
        try:
            new_soup = get_soup(new_url, browser)
        except CredentialError:
            if progress_var:
                progress_var.set(progress_var.get() + step)
            return -1

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

    address_pass = compare_address_soup(old_soup, new_soup, old_url, new_url)
    content_pass = compare_homepage_content(old_soup, new_soup, old_url, new_url)
    image_pass = check_homepage_image(new_soup, new_url)
    link_pass = check_homepage_link(old_soup, new_soup, old_url, new_url, browser=browser)
    page_pass = meta_pass and address_pass and content_pass and image_pass and link_pass

    if page_pass:
        print(new_url + " HOMEPAGE PASSED!")
        result.write(new_url + " HOMEPAGE PASSED!\n")
        result.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return True
    else:
        result.write(new_url + " HOMEPAGE FAILED! (see detail files for more information)\n")
        result.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False


# compare the text content for homepage
def compare_homepage_content(old_soup, new_soup, old_url, new_url):
    detail = open("result\\homepage_detail.txt", 'a')
    page_pass = True
    old_container1 = old_soup.find('div', id="content")
    old_container2 = old_soup.find('div', id="features")
    new_container1 = new_soup.find('div', id="content")
    new_container2 = new_soup.find('div', id="features")

    if old_container1:
        for (name, kwargs) in settings["OLD_HOMEPAGE_CONTENT_IGNORE"]:
            for s in old_container1.find_all(name, **kwargs):
                s.extract()
    if old_container2:
        for (name, kwargs) in settings["OLD_HOMEPAGE_CONTENT_IGNORE"]:
            for s in old_container2.find_all(name, **kwargs):
                s.extract()
    if new_container1:
        for (name, kwargs) in settings["NEW_HOMEPAGE_CONTENT_IGNORE"]:
            for s in new_container1.find_all(name, **kwargs):
                s.extract()
    if new_container2:
        for (name, kwargs) in settings["NEW_HOMEPAGE_CONTENT_IGNORE"]:
            for s in new_container2.find_all(name, **kwargs):
                s.extract()

    old_content = get_homepage_content(old_container1) + get_homepage_content(old_container2)
    new_content = get_homepage_content(new_container1) + get_homepage_content(new_container2)

    if new_content.find("Read More") != -1:
        entry_print("***********************************************")
        entry_print("HOMEPAGE CONTAINS 'READ MORE'!")
        entry_print("New URL: " + new_url)
        entry_print("***********************************************")
        detail.write("HOMEPAGE CONTAINS READ MORE!\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False

    old_content = old_content.replace("Read More", "Learn More").replace("Read more", "Learn More")
    old_content = old_content.replace("...", "").replace(">", "")
    new_content = new_content.replace("...", "").replace(">", "")
    old_content = old_content.replace("Learn More", "").replace("Learn more", "")
    new_content = new_content.replace("Learn More", "")
    old_content = replace_special(old_content)
    new_content = replace_special(new_content)

    if not old_content and new_content:
        record_error(old_url, "homepage container")
        detail.close()
        return False
    elif old_content and not new_content:
        record_error(new_url, "homepage container")
        detail.close()
        return False

    if old_content.replace(" ", "") != new_content.replace(" ", ""):
        entry_print("***********************************************")
        entry_print("HOMEPAGE CONTENT DIFFERENCE FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Old content: " + old_content)
        entry_print("New content: " + new_content)
        entry_print("***********************************************")
        detail.write("HOMEPAGE CONTENT DIFFERENCE FOUND!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Old content: " + old_content + "\n")
        detail.write("New content: " + new_content + "\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False
    detail.close()
    return page_pass
