# coding=utf-8
import re
from urlparse import urlparse
from config import settings
from QA_request import get_soup
from QA_util import check_format, get_domain, entry_print
from QA_error import record_error
from QA_get import get_address_soup_old, get_address_soup_new, get_meta_soup, get_content_soup_old, get_content_soup_new
from QA_util import replace_special

# module for comparing normal pages


# check the address for old url and new url
def compare_address_soup(old_soup, new_soup, old_url, new_url):
    old_address = get_address_soup_old(old_soup, old_url)
    new_address = get_address_soup_new(new_soup, new_url)
    file = open("result\\address_detail.txt", 'a')
    page_pass = True

    # number of lines different from old site
    if len(old_address) != len(new_address):
        entry_print("***********************************************")
        entry_print("NUMBER OF ADDRESSES DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Old lines: " + str(len(old_address)))
        entry_print("New lines: " + str(len(new_address)))
        entry_print("***********************************************")
        file.write("NUMBER OF ADDRESSES DIFFERENT!\n")
        file.write("Old URL: " + old_url + "\n")
        file.write("New URL: " + new_url + "\n")
        file.write("Old lines: " + str(len(old_address)) + "\n")
        file.write("New lines: " + str(len(new_address)) + "\n")
        file.write("-----------------------------------------------\n")
        file.close()
        page_pass = False
        return page_pass

    for line in range(len(old_address)):
        old_line = old_address[line]
        new_line = new_address[line]
        for ind in range(len(old_line)):
            old_detail = old_line[ind].encode('utf-8')
            new_detail = new_line[ind].encode('utf-8')

            if ind == 1:
                old_detail = old_detail.replace(",", "").replace(".", "")
                new_detail = new_detail.replace(",", "").replace(".", "")

            if old_detail != new_detail and check_format(old_detail) and old_detail != "":
                # if this is the first difference, then print header information
                if page_pass:
                    entry_print("***********************************************")
                    entry_print("ADDRESS DIFFERENCE FOUND!")
                    entry_print("Old URL: " + old_url)
                    entry_print("New URL: " + new_url)
                    file.write("ADDRESS DIFFERENCE FOUND!\n")
                    file.write("Old URL: " + old_url + "\n")
                    file.write("New URL: " + new_url + "\n")
                    page_pass = False
                entry_print("Old address: " + old_detail)
                entry_print("New address: " + new_detail)
                file.write("Old address: " + old_detail + "\n")
                file.write("New address: " + new_detail + "\n")

    if not page_pass:
        entry_print("***********************************************")
        file.write("-----------------------------------------------\n")
    file.close()
    return page_pass


# compare the metadata for old site and new site
def compare_meta_soup(old_soup, new_soup, old_url, new_url):
    page_pass = True
    file = open("result\\meta_detail.txt", "a")

    old_meta = get_meta_soup(old_soup, old_url)
    new_meta = get_meta_soup(new_soup, new_url)

    old_title = replace_special(old_meta['title'])
    new_title = replace_special(new_meta['title'])
    old_desc = replace_special(old_meta['description'])
    new_desc = replace_special(new_meta['description'])
    old_key = replace_special(old_meta['keywords'])
    new_key = replace_special(new_meta['keywords'])

    # ignore the omitted content
    if new_title.endswith("..."):
        new_title = new_title[:len(new_title) - 3]
        old_title = old_title[:len(new_title)]

    if old_desc.startswith("Learn more about"):
        old_desc = "none"

    while old_title.find("  ") != -1:
        old_title = old_title.replace("  ", " ")
    while new_title.find("  ") != -1:
        new_title = new_title.replace("  ", " ")

    title_same = old_title == new_title
    desc_same = old_desc == new_desc
    key_same = old_key == new_key

    # if the old page does not exist, then skip the site
    # (a new space page will be created in the new site)
    if old_title == "The resource cannot be found." or old_title.startswith("404"):
        title_same = True
        desc_same = True
        key_same = True

    if old_title.lower() != "page not found" and new_title == "Page Not Found":
        entry_print("***********************************************")
        entry_print("MISSING PAGE FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("***********************************************")
        file.write("-----------------------------------------------\n")
        file.write("MISSING PAGE FOUND!\n")
        file.write("Old URL: " + old_url + "\n")
        file.write("New URL: " + new_url + "\n")
        file.close()
        return -1

    if not (title_same and desc_same and key_same):
        # print and record the issue in meta.txt
        file.write("-----------------------------------------------\n")
        file.write("Old URL: " + old_url + "\n")
        file.write("New URL: " + new_url + "\n")
        entry_print("***********************************************")
        entry_print("METADATA DIFFERENCE FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        if not title_same:
            entry_print("Old title: " + old_title)
            entry_print("New title: " + new_title)
            file.write("Old title: " + old_title + "\n")
            file.write("New title: " + new_title + "\n")
        if not desc_same:
            entry_print("Old description: " + old_desc)
            entry_print("New description: " + new_desc)
            file.write("Old description: " + old_desc + "\n")
            file.write("New description: " + new_desc + "\n")
        if not key_same:
            entry_print("Old keywords: " + old_key)
            entry_print("New keywords: " + new_key)
            file.write("Old keywords: " + old_key + "\n")
            file.write("New keywords: " + new_key + "\n")
        entry_print("***********************************************")
        page_pass = False
    file.close()
    return page_pass


# compare the content of old page and new page
def compare_content_soup(old_soup, new_soup, old_url, new_url):
    page_pass = True

    old_content = get_content_soup_old(old_soup, old_url)
    new_content = get_content_soup_new(new_soup, new_url)

    if old_content is None:
        old_content = ""
    if new_content is None:
        new_content = ""

    if not old_content and new_content.startswith("We are currently"):
        return True

    if not old_content:
        old_content = ""
    if not new_content:
        new_content = ""

    old_content = replace_special(old_content)
    new_content = replace_special(new_content)

    if old_content.replace(" ", "") != new_content.replace(" ", ""):
        detail = open("result\\content_detail.txt", 'a')
        entry_print("***********************************************")
        entry_print("CONTENT DIFFERENCE FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Old content: " + old_content)
        entry_print("New content: " + new_content)
        entry_print("***********************************************")
        detail.write(
            "----------------------------------------------------------------------------------------------\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Old content: " + old_content + "\n")
        detail.write("New content: " + new_content + "\n")
        detail.close()
        page_pass = False
    return page_pass


# compare the link between old site and new site
def compare_link_soup(old_soup, new_soup, old_url, new_url, browser=None):
    detail = open("result\\site_detail.txt", 'a')
    old_hostname = urlparse(old_url).hostname
    new_hostname = urlparse(new_url).hostname

    if not old_hostname:
        old_hostname = ""
    if not new_hostname:
        new_hostname = ""

    # grab container
    old_content = old_soup.find('div', class_="right")
    new_content = new_soup.find('div', class_="right")

    if not old_content and new_content:
        if old_soup.find('div', id="content"):
            old_content = old_soup.find('div', id="content")

    if not old_content and new_content:
        record_error(old_url, "link container")
        detail.close()
        return False
    elif old_content and not new_content:
        record_error(new_url, "link container")
        detail.close()
        return False
    elif not old_content and not new_content:
        return True

    # vertical template uses different container
    if old_content.find('div', id="content"):
        old_content = old_soup.find('div', id="content")

    if new_content.find('div', id="content"):
        new_content = new_soup.find('div', id="content")

    # remove extra links from container
    if old_content:
        for (name, kwargs) in settings["COMPARE_OLD_LINK_IGNORE"]:
            for s in old_content.find_all(name, **kwargs):
                s.extract()

    if new_content:
        for (name, kwargs) in settings["COMPARE_NEW_LINK_IGNORE"]:
            for s in new_content.find_all(name, kwargs):
                s.extract()

    if old_content is None:
        old_tags = []
    else:
        old_tags = old_content.find_all('a', href=True)

    if new_content is None:
        new_tags = []
    else:
        new_tags = new_content.find_all('a', href=True)

    # remove links that does not have any content inside
    old_tags = [tag for tag in old_tags if tag.text and not tag.text.isspace() or tag.find('img')]
    new_tags = [tag for tag in new_tags if tag.text and not tag.text.isspace() or tag.find('img')]

    # check for new links that direct to old site
    host_link = old_url.replace(urlparse(old_url).path, "")
    domain = get_domain(old_url)
    new_pass1 = True
    for tag in new_tags:
        href = tag['href']
        href_hostname = urlparse(href).hostname
        if not href_hostname:
            href_hostname = ""
        if href.find(host_link) != -1 or (href_hostname.find(domain + '.') != -1 and href.find("televox.west.com") == -1) \
                or href.find("iapps") != -1:
            if new_pass1:
                entry_print("***********************************************")
                entry_print("LINKS THAT GO BACK TO OLD SITE!")
                entry_print("Old URL: " + old_url)
                entry_print("New URL: " + new_url)
                detail.write("LINKS THAT GO BACK TO OLD SITE!\n")
                detail.write("Old URL: " + old_url + "\n")
                detail.write("New URL: " + new_url + "\n")
                new_pass1 = False
            entry_print("Bad tag: " + str(tag))
            detail.write("Bad tag: " + str(tag) + "\n")
    if not new_pass1:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")

    # check for non-friendly urls
    new_pass2 = True
    for tag in new_tags:
        href = tag['href']
        if not href:
            continue
        if href.find("televox.west.com") != -1:
            if new_pass2:
                entry_print("***********************************************")
                entry_print("NON-FRIENDLY URL FOUND!")
                entry_print("New URL: " + new_url)
                detail.write("NON-FRIENDLY URL FOUND!\n")
                detail.write("New URL: " + new_url + "\n")
                new_pass2 = False
            entry_print("Bad tag: " + str(tag))
            detail.write("Bad tag: " + str(tag) + "\n")
    if not new_pass2:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")

    # remove file links
    for tag in old_tags:
        url = tag.get('href')
        if re.search("jpg|png|pdf|mp4", url):
            old_tags.remove(tag)
    for tag in new_tags:
        url = tag.get('href')
        if re.search("jpg|png|pdf|mp4|UserFile", url):
            new_tags.remove(tag)

    bad_tags = []
    if len(old_tags) != len(new_tags):
        # remove 404 pages and file links from the old tags
        for tag in old_tags:
            url = tag.get('href')
            if url is None:
                continue
            if url.startswith("https://"):
                continue
            if url.startswith("tel:") or url.startswith("mailto:") or url.find("#") != -1:
                continue
            if url.startswith("/"):
                url = "http://" + old_hostname + url
            old_target = get_soup(url)
            old_target_title = get_meta_soup(old_target, url)['title']
            if old_target_title.find("404") != -1 \
                    or re.search("page not found|the resource cannot be found", old_target_title.lower()) \
                    or old_target_title == "none":
                bad_tags.append((str(tag), old_target_title))
                old_tags.remove(tag)

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
        entry_print("INVALID LINK FOUND IN NEW SITE!")
        entry_print("New URL: " + new_url)
        detail.write("INVALID LINK FOUND IN NEW SITE!\n")
        detail.write("New URL: " + new_url + "\n")
        ind = 0
        for tag, target in new_invalid_links:
            ind += 1
            entry_print("Bad tag" + str(ind) + ": " + tag)
            entry_print("Target title: " + target)
            detail.write("Bad tag" + str(ind) + ": " + tag + "\n")
            detail.write("Target title: " + target + "\n")
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")

    # check that number of links match if not, return
    if len(new_tags) != len(old_tags):
        entry_print("***********************************************")
        entry_print("NUMBER OF LINKS DIFFERENT OR 404 LINK EXISTS IN NEW PAGE!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old links: " + str(len(old_tags)))
        entry_print("Number of new links: " + str(len(new_tags)))
        entry_print("Old tags: " + str(old_tags))
        entry_print("New tags: " + str(new_tags))
        if bad_tags:
            entry_print("404 tags in old site (removed):")
            for ind in range(len(bad_tags)):
                entry_print("Tag" + str(ind+1) + ": " + bad_tags[ind][0])
                entry_print("Target title: " + bad_tags[ind][1])
        entry_print("***********************************************")
        detail.write("NUMBER OF LINKS DIFFERENT OR 404 LINK EXISTS IN NEW PAGE!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old links: " + str(len(old_tags)) + "\n")
        detail.write("Number of new links: " + str(len(new_tags)) + "\n")
        if bad_tags:
            detail.write("404 tag(s) in old site (removed):\n")
            for ind in range(len(bad_tags)):
                detail.write("Tag" + str(ind+1) + ": " + bad_tags[ind][0] + "\n")
                detail.write("Target title: " + bad_tags[ind][1] + "\n")
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
        detail.close()
        return False

    # check that new and old links match
    new_pass3 = True
    count = 0
    for ind in range(len(new_tags)):
        old_link = old_tags[ind]['href'].replace("\\", "/").strip()
        new_link = new_tags[ind]['href'].replace("\\", "/").strip()
        if old_link == new_link:
            continue

        # take out the duplication part for old_link
        if old_link.find("#") != -1:
            old_ind = old_link.find("#")
            old_link = old_link[old_ind:]
        if new_link.find("#") != -1:
            new_ind = new_link.find("#")
            new_link = new_link[new_ind:]

        temp = old_link.split("/")
        if len(temp) > 2:
            if temp[-1] == temp[-2]:
                old_link = "/".join(temp[:-1])
        if urlparse(old_link).path == urlparse(new_link).path:
            continue

        if old_link.startswith("/"):
            old_link = "http://" + old_hostname + old_link
        # if the old link points to the homepage, then set it as "/"
        if old_link.endswith("/home") or old_link.endswith("/main"):
            old_link = "/"
        if new_link == "/home" or new_link == "/main":
            new_link = "/"
        if new_link != "/" and new_link.endswith("/"):
            new_link = new_link[:-1]
        if old_link != "/" and old_link.endswith("/"):
            old_link = old_link[:-1]

        if old_link != new_link and not new_link.startswith("/common"):
            if old_link.find("#") != -1 or new_link.find("#") != -1:
                count += 1
                if new_pass3:
                    entry_print("***********************************************")
                    entry_print("LINKS THAT DO NOT MATCH!")
                    entry_print("Old URL: " + old_url)
                    entry_print("New URL: " + new_url)
                    detail.write("LINKS THAT DO NOT MATCH!\n")
                    detail.write("Old URL: " + old_url + "\n")
                    detail.write("New URL: " + new_url + "\n")
                    new_pass3 = False
                entry_print("Old link" + str(count) + ": " + old_link)
                entry_print("New link" + str(count) + ": " + new_link)
                entry_print("Old tag" + str(count) + ": " + str(old_tags[ind]))
                entry_print("New tag" + str(count) + ": " + str(new_tags[ind]))
                detail.write("Old tag" + str(count) + ": " + str(old_tags[ind]) + "\n")
                detail.write("New tag" + str(count) + ": " + str(new_tags[ind]) + "\n")
                continue

            if old_link.startswith("/"):
                old_link = "http://" + old_hostname + old_link.strip()
            if new_link.startswith("/"):
                new_link = "http://" + new_hostname + new_link.strip()

            old_target = get_soup(old_link)
            new_target = get_soup(new_link, browser=browser)
            old_target_title = replace_special(get_meta_soup(old_target, old_link)['title'])
            new_target_title = replace_special(get_meta_soup(new_target, new_link)['title'])

            if new_target_title.endswith("..."):
                new_target_title = new_target_title[:-3]
                old_target_title = old_target_title[:len(new_target_title)]

            if old_target_title != new_target_title:
                count += 1
                if new_pass3:
                    entry_print("***********************************************")
                    entry_print("LINKS THAT DO NOT MATCH!")
                    entry_print("Old URL: " + old_url)
                    entry_print("New URL: " + new_url)
                    detail.write("LINKS THAT DO NOT MATCH!\n")
                    detail.write("Old URL: " + old_url + "\n")
                    detail.write("New URL: " + new_url + "\n")
                    new_pass3 = False
                entry_print("Old link" + str(count) + ": " + old_link)
                entry_print("New link" + str(count) + ": " + new_link)
                entry_print("Old target" + str(count) + ":" + old_target_title)
                entry_print("New target" + str(count) + ": " + new_target_title)
                entry_print("Old tag" + str(count) + ": " + str(old_tags[ind]))
                entry_print("New tag" + str(count) + ": " + str(new_tags[ind]))
                detail.write("Old tag" + str(count) + ": " + str(old_tags[ind]) + "\n")
                detail.write("New tag" + str(count) + ": " + str(new_tags[ind]) + "\n")
    if not new_pass3:
        detail.write("-----------------------------------------------\n")
        entry_print("***********************************************")

    detail.close()
    return new_pass1 and new_pass2 and new_pass3


# compare the image between old site and new site
def compare_image_soup(old_soup, new_soup, old_url, new_url):
    detail = open("result\\site_detail.txt", 'a')
    page_pass = True
    # grab container
    old_content = old_soup.find('div', class_="right")
    new_content = new_soup.find('div', class_="right")

    # check container exists and grab images
    if (not old_content or old_content.get_text().isspace()) and new_content is not None:
        if old_soup.find('div', id="content"):
            old_content = old_soup.find('div', id="content")
        else:
            old_content = old_soup.find('div', id=re.compile("Overview|overview"))

    # vertical template uses different container
    if old_content and old_content.find('div', id="content"):
        old_content = old_content.find('div', id="content")

    if new_content and new_content.find('div', id="content"):
        new_content = new_content.find('div', id="content")

    if not old_content and new_content:
        record_error(old_url, "image container")
        detail.close()
        return False
    elif old_content and not new_content:
        record_error(new_url, "image container")
        detail.close()
        return False

    # remove unnecessary tags from container
    if old_content:
        for (name, kwargs) in settings["COMPARE_OLD_IMAGE_IGNORE"]:
            for s in old_content.find_all(name, **kwargs):
                s.extract()
    if new_content:
        for (name, kwargs) in settings["COMPARE_NEW_IMAGE_IGNORE"]:
            for s in new_content.find_all(name, **kwargs):
                s. extract()

    if old_content is None:
        old_images = []
    else:
        old_images = old_content.find_all('img')

    if new_content is None:
        new_images = []
    else:
        new_images = new_content.find_all('img')

    # check that number of images are the same
    if len(new_images) != len(old_images):
        entry_print("***********************************************")
        entry_print("NUMBER OF IMAGES DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old images: " + str(len(old_images)))
        entry_print("Number of new images: " + str(len(new_images)))
        entry_print("Old images: " + str(old_images))
        entry_print("New images: " + str(new_images))
        entry_print("***********************************************")
        detail.write("NUMBER OF IMAGES DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old images: " + str(len(old_images)) + "\n")
        detail.write("Number of new images: " + str(len(new_images)) + "\n")
        detail.write("-----------------------------------------------\n")
        detail.close()
        page_pass = False
        return page_pass

    # check that images have the same class
    new_pass = True
    count = 0
    for ind in range(len(new_images)):
        old_class = old_images[ind].get('class')
        new_class = new_images[ind].get('class')

        if old_class != new_class:
            count += 1
            if new_pass:
                entry_print("***********************************************")
                entry_print("IMAGES WITH WRONG CLASS!")
                entry_print("Old URL: " + old_url)
                entry_print("New URL: " + new_url)
                detail.write("IMAGES WITH WRONG CLASS!\n")
                detail.write("Old URL: " + old_url + "\n")
                detail.write("New URL: " + new_url + "\n")
                new_pass = False
                page_pass = False
            entry_print("Old image" + str(count) + ": " + str(old_images[ind]))
            entry_print("New image" + str(count) + ": " + str(new_images[ind]))
            detail.write("Old image" + str(count) + ": " + str(old_images[ind]) + "\n")
            detail.write("New image" + str(count) + ": " + str(new_images[ind]) + "\n")
    if not new_pass:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")

    if new_content:
        for (name, kwargs) in settings["CHECKING_IMAGE_IGNORE"]:
            for s in new_content.find_all(name, **kwargs):
                s. extract()

    # check for images with id
    try:
        bad_images = list(set(new_content.find_all('img', imagesiteid=True) +
                              new_content.find_all('img', objectid=True)))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("IMAGES WITH ID FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        detail.write("IMAGES WITH ID FOUND!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
        page_pass = False

    # find images with missing alt text
    try:
        bad_images = new_content.find_all('img', alt="", src=re.compile("^((/common/)(?!(data|resource)))")) + \
                     new_content.find_all('img', alt=False, src=re.compile("^((/common/)(?!(data|resource)))"))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("IMAGES MISSING ALT TEXT FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        detail.write("IMAGES MISSING ALT TEXT FOUND!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        detail.write("-----------------------------------------------\n")
        entry_print("***********************************************")
        page_pass = False

    # find images that are not locally stored
    try:
        bad_images = new_content.find_all('img', src=re.compile(
            "^(?!.*(/common/|/UserFiles/|deardoctor|data|televoxsites)).*$"))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("IMAGES NOT LOCALLY STORED!")
        entry_print("New URL: " + new_url)
        detail.write("IMAGES NOT LOCALLY STORED!\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + '\n')
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
        page_pass = False

    detail.close()
    return page_pass
