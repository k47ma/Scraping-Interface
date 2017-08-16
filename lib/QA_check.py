# coding=utf-8
import re
import string
from urlparse import urlparse
from config import settings
from QA_util import get_domain, replace_special, entry_print
from QA_request import get_soup
from QA_get import get_meta_soup
from QA_error import record_error

# module for checking the information in new site


# check all the images for new homepage
def check_homepage_image(new_soup, new_url):
    detail = open("result\\homepage_detail.txt", 'a')
    page_pass = True
    new_content = new_soup.find('div', class_="ptl_page")

    # remove banner and navigation menu from soup
    if new_content:
        for (name, kwargs) in settings["HOMEPAGE_IMAGE_IGNORE"]:
            for s in new_content.find_all(name, **kwargs):
                s.extract()

    # find images with missing alt text
    try:
        bad_images = new_content.find_all('img', alt=lambda x: not x, src=re.compile("^((/common/)(?!(data|resource)))"))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("HOMEPAGE IMAGES WITHOUT ALT TEXT FOUND!")
        entry_print("New URL: " + new_url)
        detail.write("HOMEPAGE IMAGES WITHOUT ALT TEXT FOUND!\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        entry_print("***********************************************")
        entry_print("***********************************************\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False

    # find images that are not locally stored
    try:
        bad_images = new_content.find_all('img', src=re.compile(
            "^(?!.*(/common/|/UserFiles/|http://www.deardoctor.com|data|televoxsites)).*$"))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("HOMEPAGE IMAGES NOT LOCALLY STORED!")
        entry_print("New URL: " + new_url)
        detail.write("HOMEPAGE IMAGES NOT LOCALLY STORED!\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
        page_pass = False

    # check for images with id
    try:
        bad_images = list(set(new_content.find_all('img', imagesiteid=True) +
                              new_content.find_all('img', objectid=True)))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("HOMEPAGE IMAGES WITH ID FOUND!")
        entry_print("New URL: " + new_url)
        detail.write("HOMEPAGE IMAGES WITH ID FOUND!\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
        page_pass = False
    detail.close()
    return page_pass


# check all the links for homepage
def check_homepage_link(old_soup, new_soup, old_url, new_url, browser=None):
    detail = open("result\\homepage_detail.txt", 'a')
    old_hostname = urlparse(old_url).hostname
    new_hostname = urlparse(new_url).hostname
    page_pass = True
    printable = set(string.printable)
    new_content = new_soup.find('div', class_="ptl_page")

    if old_url.endswith("/"):
        old_url = old_url[:-1]
    if new_url.endswith("/"):
        new_url = new_url[:-1]

    if not old_hostname:
        old_hostname = old_url
    if not new_hostname:
        new_hostname = new_url

    if not new_content:
        record_error(new_url, "new homepage container")
        return False

    # remove banner and navigation menu from soup
    if new_content:
        for (name, kwargs) in settings["HOMEPAGE_LINK_IGNORE"]:
            for s in new_content.find_all(name, **kwargs):
                s.extract()

    new_tags = new_content.find_all('a', href=re.compile("^(?!.*(#aftermap|#)).*$"))

    # check for new links that direct to old site
    host_link = old_url.replace(urlparse(old_url).path, "")
    domain = get_domain(old_url)
    for tag in new_tags:
        href = tag['href']
        href_hostname = urlparse(href).hostname
        if href_hostname is None:
            href_hostname = ""
        if href.startswith("/"):
            continue
        if (href.startswith(host_link) and host_link != "") \
                or (href_hostname.find(domain + '.') != -1 and not href.startswith("mailto") and href.find("televox.west.com") == -1) \
                or href.find("iapps") != -1:
            page_pass = False
            entry_print("***********************************************")
            entry_print("HOMEPAGE LINKS THAT GO BACK TO OLD SITE!")
            entry_print("New URL: " + new_url)
            detail.write("HOMEPAGE LINKS THAT GO BACK TO OLD SITE!\n")
            detail.write("New URL: " + new_url + "\n")
            entry_print("Bad tag: " + str(tag))
            entry_print("***********************************************")
            detail.write("Bad tag: " + str(tag) + "\n")
            detail.write("-----------------------------------------------\n")
        if href.find("televox.west.com") != -1:
            page_pass = False
            entry_print("***********************************************")
            entry_print("NON-FRIENDLY URL FOUND! ")
            entry_print("New URL: " + new_url)
            detail.write("NON-FRIENDLY URL FOUND!\n")
            detail.write("New URL: " + new_url + "\n")
            entry_print("Bad tag: " + str(tag))
            entry_print("***********************************************")
            detail.write("Bad tag: " + str(tag) + "\n")
            detail.write("-----------------------------------------------\n")

    # check invalid links in new site
    new_invalid_links = []
    for tag in new_tags:
        url = tag.get('href')
        if url is None:
            continue
        if url.startswith("https://"):
            continue
        if url.startswith("tel:") or url.startswith("mailto:") or url.find("#") != -1 or url.startswith("/common"):
            continue
        if url.startswith("/"):
            url = "http://" + new_hostname + url
        if url.find("televox.west.com") != -1:
            new_target = get_soup(url, browser)
        else:
            new_target = get_soup(url)
        new_target_title = get_meta_soup(new_target, url)['title']
        if new_target_title.find("404") != -1 or new_target_title == "Page Not Found" or new_target_title == "none":
            new_invalid_links.append((str(tag), new_target_title))

    if new_invalid_links:
        entry_print("***********************************************")
        entry_print("INVALID LINK FOUND IN HOMEPAGE!")
        entry_print("New URL: " + new_url)
        detail.write("-----------------------------------------------\n")
        detail.write("INVALID LINK FOUND IN HOMEPAGE!\n")
        detail.write("New URL: " + new_url + "\n")
        ind = 0
        for tag, target in new_invalid_links:
            ind += 1
            entry_print("Bad tag" + str(ind) + ": " + tag)
            entry_print("Target title: " + target)
            detail.write("Bad tag" + str(ind) + ": " + tag + "\n")
            detail.write("Target title: " + target + "\n")
        entry_print("***********************************************")

    # check published links for homepage
    old_publish = old_soup.find('nav', id="utility-navigation")
    new_publish = new_soup.find('nav', id="utility-navigation")

    if old_publish:
        old_published_links = old_publish.find_all('a', href=re.compile("^((?!#).)*$"))
    else:
        old_published_links = []
    if new_publish:
        new_published_links = new_publish.find_all('a', href=re.compile("^((?!#).)*$"))
    else:
        new_published_links = []

    if len(old_published_links) != len(new_published_links):
        entry_print("***********************************************")
        entry_print("NUMBER OF PUBLISHED LINKS DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old links: " + str(len(old_published_links)))
        entry_print("Number of new links: " + str(len(new_published_links)))
        entry_print("***********************************************")
        detail.write("NUMBER OF PUBLISHED LINKS DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old links: " + str(len(old_published_links)) + "\n")
        detail.write("Number of new links: " + str(len(new_published_links)) + "\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False
    else:
        publish_pass = True
        # check the href and name for each published link
        for ind in range(len(new_published_links)):
            old_link = old_published_links[ind]['href']
            new_link = new_published_links[ind]['href']
            old_link_dup = old_link.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            new_link_dup = new_link.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            old_name = old_published_links[ind].get_text().replace("  ", " ")
            new_name = new_published_links[ind].get_text().replace("  ", " ")
            old_name = "".join([i for i in old_name if i in printable]).strip().upper()
            new_name = "".join([i for i in new_name if i in printable]).strip().upper()
            old_name_dup = old_name.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            new_name_dup = new_name.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if old_link_dup != new_link_dup:
                if old_link.startswith("tel:") or old_link.startswith("mailto:") or unicode(old_link[0]).isnumeric():
                    continue

                if old_link.startswith("/"):
                    old_link = old_hostname + old_link
                if new_link.startswith("/"):
                    new_link = new_hostname + new_link

                old_target = get_soup(old_link)
                new_target = get_soup(new_link, browser=browser)
                old_target_title = get_meta_soup(old_target, old_link)['title']
                new_target_title = get_meta_soup(new_target, new_link)['title']

                if new_target_title.endswith("..."):
                    new_target_title = new_target_title[:-3]
                    old_target_title = old_target_title[:len(new_target_title)]

                if old_target_title != new_target_title:
                    if publish_pass:
                        entry_print("***********************************************")
                        entry_print("PUBLISHED LINKS DO NOT MATCH!")
                        entry_print("Old URL: " + old_url)
                        entry_print("New URL: " + new_url)
                        detail.write("PUBLISHED LINKS DO NOT MATCH!\n")
                        detail.write("Old URL: " + old_url + "\n")
                        detail.write("New URL: " + new_url + "\n")
                        publish_pass = False
                        page_pass = False
                    entry_print("Old link: " + old_link)
                    entry_print("New link: " + new_link)
                    detail.write("Old link: " + old_link + "\n")
                    detail.write("New link: " + new_link + "\n")
            if old_name_dup != new_name_dup:
                if publish_pass:
                    entry_print("***********************************************")
                    entry_print("PUBLISHED LINK NAMES DO NOT MATCH!")
                    entry_print("Old URL: " + old_url)
                    entry_print("New URL: " + new_url)
                    detail.write("PUBLISHED LINK NAMES DO NOT MATCH!\n")
                    detail.write("Old URL: " + old_url + "\n")
                    detail.write("New URL: " + new_url + "\n")
                    publish_pass = False
                    page_pass = False
                entry_print("Old name: " + old_name)
                entry_print("New name: " + new_name)
                detail.write("Old name: " + old_name + "\n")
                detail.write("New name: " + new_name + "\n")
        if not publish_pass:
            entry_print("***********************************************")
            detail.write("-----------------------------------------------\n")

    # check social media links for homepage
    old_social = old_soup.find('nav', class_="social-navigation")
    new_social = new_soup.find('nav', class_="social-navigation")

    if old_social:
        old_social_links = old_social.find_all('a')
    else:
        old_social_links = []
    if new_social:
        new_social_links = new_social.find_all('a')
    else:
        new_social_links = []

    if len(old_social_links) != len(new_social_links):
        entry_print("***********************************************")
        entry_print("NUMBER OF SOCIAL LINKS DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old links: " + str(len(old_social_links)))
        entry_print("Number of new links: " + str(len(new_social_links)))
        entry_print("***********************************************")
        detail.write("NUMBER OF SOCIAL LINKS DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old links: " + str(len(old_social_links)) + "\n")
        detail.write("Number of new links: " + str(len(new_social_links)) + "\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False
    else:
        social_pass = True
        # check the href and name for each social link
        for ind in range(len(new_social_links)):
            old_link = old_social_links[ind]['href']
            new_link = new_social_links[ind]['href']
            old_link_reversed = old_social_links[len(old_social_links) - ind - 1]['href']
            if old_link != new_link and old_link_reversed != new_link:
                if new_link.startswith("/"):
                    new_link = new_hostname + new_link
                if old_link.startswith("/"):
                    old_link = old_hostname + old_link

                old_target = get_soup(old_link)
                new_target = get_soup(new_link)
                old_target_title = replace_special(get_meta_soup(old_target, old_link)['title'])
                new_target_title = replace_special(get_meta_soup(new_target, new_link)['title'])

                if new_target_title.endswith("..."):
                    new_target_title = new_target_title[:-3]
                    old_target_title = old_target_title[:len(new_target_title)]

                if old_target_title != new_target_title:
                    if social_pass:
                        entry_print("***********************************************")
                        entry_print("SOCIAL LINKS DO NOT MATCH!")
                        entry_print("Old URL: " + old_url)
                        entry_print("New URL: " + new_url)
                        detail.write("SOCIAL LINKS DO NOT MATCH!\n")
                        detail.write("Old URL: " + old_url + "\n")
                        detail.write("New URL: " + new_url + "\n")
                        social_pass = False
                    entry_print("Old target: " + old_target_title)
                    entry_print("New target: " + new_target_title)
                    entry_print("Old link: " + old_link)
                    entry_print("New link: " + new_link)
                    detail.write("Old link: " + old_link + "\n")
                    detail.write("New link: " + new_link + "\n")
        if not social_pass:
            entry_print("***********************************************")
            detail.write("-----------------------------------------------\n")
    detail.close()
    return page_pass
