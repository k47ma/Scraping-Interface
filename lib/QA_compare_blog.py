# coding=utf-8
import re
import string
from ThreadPool import ThreadPool
from urlparse import urlparse
from config import *
from QA_util import replace_special, get_domain, entry_print
from QA_request import get_soup
from QA_get import get_meta_soup, get_blog_content
from QA_error import record_error
from QA_compare_normal import compare_meta_soup


# modules for comparing information for blogs


# compare blog page (index page) and start comparing blog posts
def compare_blog(old_soup, new_soup, old_url, new_url, browser=None, progress_var=None, step=50.0):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    detail = open("result\\blog_detail.txt", 'a')

    meta_pass = compare_meta_soup(old_soup, new_soup, old_url, new_url)

    old_content = old_soup.find('ul', class_="content-list")
    new_content = new_soup.find('div', class_="divContent")

    # cannot find blog containers
    if old_content is None or new_content is None:
        if old_content is None and new_content is None:
            if progress_var:
                progress_var.set(progress_var.get() + step)
            detail.close()
            return True
        elif old_content is None:
            record_error(old_url, "blog entries")
            if progress_var:
                progress_var.set(progress_var.get() + step)
            detail.close()
            return False
        elif new_content is None:
            record_error(new_url, "blog entries")
            if progress_var:
                progress_var.set(progress_var.get() + step)
            detail.close()
            return False

    # get post links from blog page
    old_posts = old_content.find_all('a', href=re.compile("^((?!#comments).)*$"))
    new_posts = new_content.find_all('a', href=True, title=re.compile("^((?!Read More).)*$"), class_="title")

    # filter out links for featured images
    for post in old_posts:
        if post.find('img'):
            old_posts.remove(post)

    # print out site information
    if len(old_posts) == len(new_posts):
        entry_print("Number of blog posts: " + str(len(old_posts)), True)
    else:
        entry_print("Number of old blog posts: " + str(len(old_posts)), True)
        entry_print("Number of new blog posts: " + str(len(new_posts)), True)

    old_titles = [post.get_text() for post in old_posts]
    new_titles = [post.get_text() for post in new_posts]

    # missing blog posts
    if len(old_posts) != len(new_posts):
        entry_print("***********************************************")
        entry_print("NUMBER OF BLOG POSTS DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old posts: " + str(len(old_posts)))
        entry_print("Number of new posts: " + str(len(new_posts)))
        entry_print("Old posts: " + str(old_titles))
        entry_print("New posts: " + str(new_titles))
        entry_print("***********************************************")
        detail.write("NUMBER OF BLOG POSTS DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old posts: " + str(len(old_posts)) + "\n")
        detail.write("Number of new posts: " + str(len(new_posts)) + "\n")
        detail.write("Old posts: " + str(old_titles) + "\n")
        detail.write("New posts: " + str(new_titles) + "\n")
        detail.write("-----------------------------------------------\n")
        detail.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False

    # avoid divided by zero error
    if len(old_posts) == 0:
        if progress_var:
            progress_var.set(progress_var.get() + step)
        detail.close()
        return True

    old_dic = {}
    old_list = []
    ind = 1
    for old_post in old_posts:
        title = replace_special(old_post.get_text())
        link = old_post.get('href')
        if title in old_dic:
            old_dic[title + str(ind)] = link
            old_list.append((title + str(ind), link))
            ind += 1
        else:
            old_dic[title] = link
            old_list.append((title, link))

    new_dic = {}
    new_list = []
    ind = 1
    for new_post in new_posts:
        title = replace_special(new_post.get_text())
        link = new_post.get('href')
        if title in new_dic:
            new_dic[title + str(ind)] = link
            new_list.append((title + str(ind), link))
            ind += 1
        else:
            new_dic[title] = link
            new_list.append((title + str(ind), link))

    title_pass = compare_blog_title(old_posts, new_posts, old_url, new_url)
    summary_pass = compare_blog_summary(old_soup, new_soup, old_url, new_url)
    posts_pass = compare_blog_posts_thread(old_dic, new_dic, old_list, new_list, old_url, new_url, browser=browser,
                                           progress_var=progress_var, step=step)

    blog_pass = meta_pass and title_pass and summary_pass and posts_pass

    if blog_pass:
        print(new_url + " BLOG PASSED!")
    detail.close()
    return blog_pass


# check everything for each blog post
def compare_blog_posts_thread(old_dic, new_dic, old_list, new_list, old_url, new_url, browser=None, progress_var=None,
                              step=50.0):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    thread_pool = ThreadPool(settings["THREADPOOL_SIZE"])
    posts_pass = True
    new_hostname = urlparse(new_url).hostname

    post_step = step / len(old_list)

    for ind in range(len(old_list)):
        old_title = old_list[ind][0]
        old_link = old_list[ind][1]

        if new_list[ind][0] == old_list[ind][0]:
            new_link = new_list[ind][1]
        else:
            try:
                new_link = new_dic[old_title]
            except KeyError:
                new_link = new_list[ind][1]

        if new_link.startswith('/'):
            new_link = "http://" + new_hostname + new_link

        if browser:
            post_pass = compare_blog_page_thread(old_link, new_link, browser=browser, progress_var=progress_var,
                                                 step=post_step)
        else:
            thread_pool.add_task(compare_blog_page_thread, old_url=old_link, new_url=new_link,
                                 progress_var=progress_var, step=post_step)

    thread_pool.wait_completion()
    thread_pool.destroy()

    return posts_pass


# compare everything for the blog post
def compare_blog_page_thread(old_url, new_url, browser=None, progress_var=None, step=1.0):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    detail = open("result\\blog_detail.txt", 'a')
    blog_pass = True

    old_soup = get_soup(old_url)
    new_soup = get_soup(new_url, browser)

    if old_soup is None:
        record_error(old_url, "soup")
        detail.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False
    if new_soup is None:
        record_error(new_url, "soup")
        detail.close()
        if progress_var:
            progress_var.set(progress_var.get() + step)
        return False

    new_content = new_soup.find('div', class_="right")

    if new_content.find('div', id="content"):
        new_content = new_content.find('div', id="content")

    try:
        if new_content.find('header'):
            entry_print("***********************************************")
            entry_print("BLOG HEADER FOUND!")
            entry_print("Old URL: " + old_url)
            entry_print("New URL: " + new_url)
            entry_print("***********************************************")
            detail.write("BLOG HEADER FOUND!\n")
            detail.write("Old URL: " + old_url + "\n")
            detail.write("New URL: " + new_url + "\n")
            detail.write("-----------------------------------------------\n")
            blog_pass = False
    except AttributeError:
        pass

    image_pass = compare_blog_image(old_soup, new_soup, old_url, new_url)
    link_pass = compare_blog_link(old_soup, new_soup, old_url, new_url, browser=browser)
    content_pass = compare_blog_content(old_soup, new_soup, old_url, new_url)
    meta_pass = compare_meta_soup(old_soup, new_soup, old_url, new_url)

    blog_pass = blog_pass and image_pass and link_pass and content_pass and meta_pass
    detail.close()

    if blog_pass:
        print(new_url + " BLOG PAGE PASSED!")

    if progress_var:
        progress_var.set(progress_var.get() + step)

    return blog_pass


# compare blog titles
def compare_blog_title(old_posts, new_posts, old_url, new_url):
    detail = open("result\\blog_detail.txt", 'a')
    title_pass = True

    old_titles = [replace_special(tag.get_text()) for tag in old_posts]
    new_titles = [replace_special(tag.get_text()) for tag in new_posts]

    # compare the content of each title
    for ind in range(len(old_titles)):
        # remove special characters
        old_title = old_titles[ind]
        new_title = new_titles[ind]

        if old_title != new_title and old_title not in new_titles:
            if title_pass:
                entry_print("***********************************************")
                entry_print("BLOG TITLE DIFFERENT!")
                entry_print("Old URL: " + old_url)
                entry_print("New URL: " + new_url)
                detail.write("BLOG TITLE DIFFERENT!\n")
                detail.write("Old URL: " + old_url + "\n")
                detail.write("New URL: " + new_url + "\n")
                title_pass = False
            entry_print("Old title: " + old_title)
            entry_print("New title: " + new_title)
            detail.write("Old title: " + old_title + "\n")
            detail.write("New title: " + new_title + "\n")
    if not title_pass:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
    detail.close()
    return title_pass


# compare blog summaries
def compare_blog_summary(old_soup, new_soup, old_url, new_url):
    detail = open("result\\blog_detail.txt", 'a')
    summary_pass = True
    printable = set(string.printable)

    old_posts = old_soup.find('div', class_="right").find('div', class_="left").find_all('p', class_=False)
    new_posts = new_soup.find_all('div', class_="summary", text=True)

    old_summaries = [post.get_text() for post in old_posts]
    new_summaries = [post.get_text() for post in new_posts]

    # check the number of summaries
    if len(old_summaries) != len(new_summaries):
        entry_print("***********************************************")
        entry_print("NUMBER OF BLOG SUMMARIES DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Old summaries: " + str(len(old_summaries)))
        entry_print("New summaries: " + str(len(new_summaries)))
        entry_print("***********************************************")
        detail.write("NUMBER OF BLOG SUMMARIES DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Old summaries: " + str(len(old_summaries)) + "\n")
        detail.write("New summaries: " + str(len(new_summaries)) + "\n")
        detail.write("-----------------------------------------------\n")
        detail.close()
        return False

    # compare the content of each summary
    for ind in range(len(old_summaries)):
        # remove special characters
        old_summary = old_summaries[ind]
        new_summary = new_summaries[ind]
        old_summary = "".join([i for i in old_summary if i in printable]).strip()
        new_summary = "".join([i for i in new_summary if i in printable]).strip()
        old_summary = replace_special(old_summary)
        new_summary = replace_special(new_summary)

        if old_summary != new_summary and old_summary not in new_summaries:
            if summary_pass:
                entry_print("***********************************************")
                entry_print("BLOG SUMMARY DIFFERENT!")
                entry_print("Old URL: " + old_url)
                entry_print("New URL: " + new_url)
                detail.write("BLOG SUMMARY DIFFERENT!\n")
                detail.write("Old URL: " + old_url + "\n")
                detail.write("New URL: " + new_url + "\n")
                summary_pass = False
            entry_print("Old summary: " + old_summary)
            entry_print("New summary: " + new_summary)
            detail.write("Old summary: " + old_summary + "\n")
            detail.write("New summary: " + new_summary + "\n")
    if not summary_pass:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
    detail.close()
    return summary_pass


# compare the images for blog post
def compare_blog_image(old_soup, new_soup, old_url, new_url):
    detail = open("result\\blog_detail.txt", 'a')
    page_pass = True
    old_content = old_soup.find('article')
    new_content = new_soup.find('div', class_="right")

    if new_content.find('div', id="content"):
        new_content = new_content.find('div', id="content")

    if old_content:
        for (name, kwargs) in settings["OLD_BLOG_IMAGE_IGNORE"]:
            for s in old_content.find_all(name, **kwargs):
                s.extract()

    if new_content:
        for (name, kwargs) in settings["NEW_BLOG_IMAGE_IGNORE"]:
            for s in new_content.find_all(name, **kwargs):
                s.extract()

    old_images = old_content.find_all('img')
    new_images = new_content.find_all('img')

    # check that number of images are the same
    if len(new_images) != len(old_images):
        entry_print("***********************************************")
        entry_print("NUMBER OF BLOG IMAGES DIFFERENT!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Number of old images: " + str(len(old_images)))
        entry_print("Number of new images: " + str(len(new_images)))
        entry_print("***********************************************")
        detail.write("NUMBER OF BLOG IMAGES DIFFERENT!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old images: " + str(len(old_images)) + "\n")
        detail.write("Number of new images: " + str(len(new_images)) + "\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False
        detail.close()
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
                entry_print("BLOG IMAGES WITH WRONG CLASS!")
                entry_print("Old URL: " + old_url)
                entry_print("New URL: " + new_url)
                detail.write("BLOG IMAGES WITH WRONG CLASS!\n")
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
                s.extract()

    # check for images with id
    try:
        bad_images = list(set(new_content.find_all('img', imagesiteid=True) +
                              new_content.find_all('img', objectid=True)))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("BLOG IMAGES WITH ID FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        detail.write("BLOG IMAGES WITH ID FOUND!\n")
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
        bad_images = new_content.find_all('img', alt=lambda x: not x,
                                          src=re.compile("^((/common/)(?!(data|resource)))"))
    except AttributeError:
        bad_images = []
    if bad_images:
        entry_print("***********************************************")
        entry_print("BLOG IMAGES MISSING ALT TEXT FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        detail.write("BLOG IMAGES MISSING ALT TEXT FOUND!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        entry_print("***********************************************")
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
        entry_print("BLOG IMAGES NOT LOCALLY STORED!")
        entry_print("New URL: " + new_url)
        detail.write("BLOG IMAGES NOT LOCALLY STORED!\n")
        detail.write("New URL: " + new_url + "\n")
        for image in bad_images:
            entry_print("Bad image: " + str(image))
            detail.write("Bad image: " + str(image) + "\n")
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
        page_pass = False

    detail.close()
    return page_pass


# check all the links for blog page
def compare_blog_link(old_soup, new_soup, old_url, new_url, browser=None):
    detail = open("result\\blog_detail.txt", 'a')
    domain = get_domain(old_url)
    old_hostname = urlparse(old_url).hostname
    new_hostname = domain + ".televox.west.com"
    old_content = old_soup.find('article')
    new_content = new_soup.find('div', class_="right")

    if new_content.find('div', id="content"):
        new_content = new_content.find('div', id="content")

    # check that container exists and grab links
    if old_content is None and new_content is not None:
        old_content = old_soup.find('div', class_="overview")

    if old_content:
        for (name, kwargs) in settings["OLD_BLOG_LINK_IGNORE"]:
            for s in old_content.find_all(name, **kwargs):
                s.extract()
    if new_content:
        for (name, kwargs) in settings["NEW_BLOG_LINK_IGNORE"]:
            for s in new_content.find_all(name, **kwargs):
                s.extract()

    old_tags = old_content.find_all('a', href=lambda x: x is not None and x.find("#") == -1,
                                    text=lambda x: x and not x.isspace())
    new_tags = new_content.find_all('a', href=True, text=lambda x: x and not x.isspace())

    # check for new links that direct to old site
    host_link = old_url.replace(urlparse(old_url).path, "")
    domain = get_domain(old_url)
    new_pass1 = True
    for tag in new_tags:
        href = tag['href']
        if href.startswith(host_link) or (href.find(domain + '.') != -1 and not href.startswith("mailto")) or href.find(
                "iapps") != -1:
            if new_pass1:
                entry_print("***********************************************")
                entry_print("BLOG LINKS THAT GO BACK TO OLD SITE OR NON-FRIENDLY URL FOUND!")
                entry_print("Old URL: " + old_url)
                entry_print("New URL: " + new_url)
                detail.write("BLOG LINKS THAT GO BACK TO OLD SITE OR NON-FRIENDLY URL FOUND!\n")
                detail.write("Old URL: " + old_url + "\n")
                detail.write("New URL: " + new_url + "\n")
                new_pass1 = False
            entry_print("Bad tag: " + str(tag))
            detail.write("Bad tag: " + str(tag) + "\n")
    if not new_pass1:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")

    # remove 404 pages from the old tags
    bad_tags = []
    for tag in old_tags:
        url = tag.get('href')
        if url is None:
            continue
        if url.startswith("https://"):
            continue
        if url.startswith("tel:") or url.startswith("mailto:"):
            continue
        if url.startswith("/"):
            url = old_hostname + url
        old_target = get_soup(url)
        old_target_title = get_meta_soup(old_target, url)['title']
        if old_target_title.find("404") != -1 or old_target_title.lower().find(
                "page not found") != -1 or old_target_title == "none":
            bad_tags.append((str(tag), old_target_title))
            old_tags.remove(tag)

    # check that number of links match if not, return
    if len(new_tags) != len(old_tags):
        entry_print("***********************************************")
        entry_print("NUMBER OF BLOG LINKS DIFFERENT OR 404 LINK EXISTS IN NEW BLOG PAGE!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Old tags: " + str(old_tags))
        entry_print("New tags: " + str(new_tags))
        entry_print("Number of old links: " + str(len(old_tags)))
        entry_print("Number of new links: " + str(len(new_tags)))
        if bad_tags:
            entry_print("404 tags in old site (removed):")
            for ind in range(len(bad_tags)):
                entry_print("Tag" + str(ind + 1) + ": " + bad_tags[ind][0])
                entry_print("Target title: " + bad_tags[ind][1])
        entry_print("***********************************************")
        detail.write("NUMBER OF BLOG LINKS DOES NOT MATCH OR 404 LINK EXISTS IN NEW BLOG PAGE!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Number of old links: " + str(len(old_tags)) + "\n")
        detail.write("Number of new links: " + str(len(new_tags)) + "\n")
        if bad_tags:
            detail.write("404 tag(s) in old site (removed):\n")
            for ind in range(len(bad_tags)):
                detail.write("Tag" + str(ind + 1) + ": " + bad_tags[ind][0] + "\n")
                detail.write("Target title: " + bad_tags[ind][1] + "\n")
        detail.write("-----------------------------------------------\n")
        detail.close()
        return False

    # check 404 pages in new site
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
        if new_target_title.find("404") != -1 or new_target_title == "Page Not Found" or new_target_title == "none" \
                or new_target_title == "The resource cannot be found.":
            new_invalid_links.append((str(tag), new_target_title))

    if new_invalid_links:
        entry_print("***********************************************")
        entry_print("INVALID LINK FOUND IN NEW BLOG!")
        entry_print("New URL: " + new_url)
        detail.write("-----------------------------------------------\n")
        detail.write("INVALID LINK FOUND IN NEW BLOG!\n")
        detail.write("New URL: " + new_url + "\n")
        ind = 0
        for tag, target in new_invalid_links:
            ind += 1
            entry_print("Bad tag" + str(ind) + ": " + tag)
            entry_print("Target title: " + target)
            detail.write("Bad tag" + str(ind) + ": " + tag + "\n")
            detail.write("Target title: " + target + "\n")
        entry_print("***********************************************")

    # check that new and old links match
    new_pass2 = True
    count = 0
    for ind in range(len(new_tags)):
        old_link = replace_special(old_tags[ind]['href'].replace("\\", "/").replace(u" ", ""))
        new_link = replace_special(new_tags[ind]['href'].replace("\\", "/").replace(u" ", ""))

        if not old_link:
            old_link = ""
        if not new_link:
            new_link = ""

        if old_link == new_link:
            continue

        # take out the duplication part for old_link
        temp = old_link.split("/")
        if len(temp) > 2:
            if temp[-1] == temp[-2]:
                old_link = "/".join(temp[:-1])
        if urlparse(old_link).path == urlparse(new_link).path:
            continue

        # if the old link points to the homepage, then set it to be "/"
        if old_link.endswith("/home") or old_link.endswith("/main"):
            old_link = "/"
        if new_link == "/home" or new_link == "/main":
            new_link = "/"
        if new_link != "/" and new_link.endswith("/"):
            new_link = new_link[:-1]
        if old_link != "/" and old_link.endswith("/"):
            old_link = old_link[:-1]

        if old_link != new_link and not new_link.startswith("/common"):
            if old_link.startswith("/"):
                old_link = "http://" + old_hostname + old_link
            if new_link.startswith("/"):
                new_link = "http://" + new_hostname + new_link

            old_target = get_soup(old_link)
            new_target = get_soup(new_link, browser=browser)
            old_target_title = get_meta_soup(old_target, old_link)['title']
            new_target_title = get_meta_soup(new_target, new_link)['title']

            if new_target_title.endswith("..."):
                new_target_title = new_target_title[:-3]
                old_target_title = old_target_title[:len(new_target_title)]

            if old_target_title != new_target_title and old_target_title != "The resource cannot be found." \
                    and old_target_title.find("404") == -1:
                count += 1
                if new_pass2:
                    entry_print("***********************************************")
                    entry_print("BLOG LINKS THAT DO NOT MATCH!")
                    entry_print("Old URL: " + old_url)
                    entry_print("New URL: " + new_url)
                    detail.write("BLOG LINKS THAT DO NOT MATCH!\n")
                    detail.write("Old URL: " + old_url + "\n")
                    detail.write("New URL: " + new_url + "\n")
                    new_pass2 = False
                entry_print("Old link" + str(count) + ": " + old_link)
                entry_print("New link" + str(count) + ": " + new_link)
                entry_print("Old target" + str(count) + ": " + old_target_title)
                entry_print("New target" + str(count) + ": " + new_target_title)
                entry_print("Old tag" + str(count) + ": " + str(old_tags[ind]))
                entry_print("New tag" + str(count) + ": " + str(new_tags[ind]))
                detail.write("Old tag" + str(count) + ": " + str(old_tags[ind]) + "\n")
                detail.write("New tag" + str(count) + ": " + str(new_tags[ind]) + "\n")
    if not new_pass2:
        entry_print("***********************************************")
        detail.write("-----------------------------------------------\n")
    detail.close()
    return new_pass1 and new_pass2


# compare content for blog page
def compare_blog_content(old_soup, new_soup, old_url, new_url):
    detail = open("result\\blog_detail.txt", 'a')
    page_pass = True
    old_container = old_soup.find('article')
    new_container = new_soup.find('div', id="news_content_body")

    if old_container:
        for (name, kwargs) in settings["OLD_BLOG_CONTENT_IGNORE"]:
            for s in old_container.find_all(name, **kwargs):
                s.extract()

    if new_container:
        for (name, kwargs) in settings["NEW_BLOG_CONTENT_IGNORE"]:
            for s in new_container.find_all(name, **kwargs):
                s.extract()

    old_content = get_blog_content(old_container)
    new_content = get_blog_content(new_container)

    if not old_content and new_content:
        record_error(old_url, "blog container")
        detail.close()
        return False
    elif old_content and not new_content:
        record_error(new_url, "blog container")
        detail.close()
        return False

    if not old_content and new_content.startswith("We are currently"):
        detail.close()
        return True

    if old_content.replace(" ", "") != new_content.replace(" ", ""):
        entry_print("***********************************************")
        entry_print("BLOG CONTENT DIFFERENCE FOUND!")
        entry_print("Old URL: " + old_url)
        entry_print("New URL: " + new_url)
        entry_print("Old content: " + old_content)
        entry_print("New content: " + new_content)
        entry_print("***********************************************")
        detail.write("BLOG CONTENT DIFFERENCE FOUND!\n")
        detail.write("Old URL: " + old_url + "\n")
        detail.write("New URL: " + new_url + "\n")
        detail.write("Old content: " + old_content + "\n")
        detail.write("New content: " + new_content + "\n")
        detail.write("-----------------------------------------------\n")
        page_pass = False
    detail.close()
    return page_pass
