# coding=utf-8
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from requests import ConnectionError
from requests.exceptions import InvalidURL, ContentDecodingError
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from config import *
from QA_error import record_error, CredentialError
from QA_util import entry_print

# module for sending HTTP requests and returning soups


# retrieve data from site and return the soup
def get_soup(url, browser=None):
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url

    if re.search("pdf|jpg|png|mp4|tel:|mailto:|/UserFile", url):
        return None

    # use selenium to retrieve the data
    if browser:
        return get_soup_selenium(url, browser)

    try:
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "html.parser")
    except ConnectionError:
        if url[7:].startswith("www."):
            return None
        new_link = url[:7] + "www." + url[7:]
        entry_print("Bad URL! Trying " + new_link)
        return get_soup(new_link)
    except ContentDecodingError:
        record_error(url, "site")
        return None
    except InvalidURL:
        record_error(url, "site")
        return None
    except OverflowError:
        record_error(url, "site")
        return None

    if soup is not None:
        if url.find("televox.west.com") != -1:
            for (name, kwargs) in settings["GET_NEW_SOUP_IGNORE"]:
                for s in soup.find_all(name, **kwargs):
                    s.extract()
        else:
            for (name, kwargs) in settings["GET_OLD_SOUP_IGNORE"]:
                for s in soup.find_all(name, **kwargs):
                    s.extract()

    return soup


# get a list of relative url from the site map of old site
def get_sites(url, browser=None):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return None

    if url.endswith("/"):
        url = url[:-1]
    url += "/pagesitemap.xml"

    soup = get_soup(url, browser)

    try:
        url_tags = soup.find_all('loc')
    except AttributeError:
        url = "http://" + urlparse(url).hostname + "/sitemap.xml"
        soup = get_soup(url, browser)
        url_tags = soup.find_all('loc')

    if not url_tags:
        url = "http://" + urlparse(url).hostname + "/sitemap.xml"
        soup = get_soup(url, browser)
        url_tags = soup.find_all('loc')

    url_list = []

    for tag in url_tags:
        page_url = urlparse(tag.get_text()).path
        url_split = page_url.split("/")
        if len(url_split) > 2 and url_split[-1] == url_split[-2]:
            continue
        if page_url.find("site-map") != -1:
            continue
        if page_url == "/":
            continue
        if page_url.find("blog") == -1:
            url_list.append(page_url)
    return url_list


def get_blog_site(url, browser=None):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return None

    if url.endswith("/"):
        url = url[:-1]

    # url is for old site
    if url.find("televox.west.com") == -1:
        url += "/pagesitemap.xml"
    # url is for new site
    else:
        url += "/sitemap.xml"

    soup = get_soup(url, browser=browser)

    url_tags = soup.find_all('loc')

    for tag in url_tags:
        page_url = tag.get_text()
        if page_url.find("blog") != -1 and page_url.find("blog/") == -1:
            return page_url
    return None


# use Selenium to retrieve data
def get_soup_selenium(url, browser):
    wait = WebDriverWait(browser, 20)

    if re.search("pdf|jpg|png|mp4|tel:|mailto:|/UserFile", url):
        return None

    try:
        browser.get(url)
    except WebDriverException:
        return None

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return None

    # use Selenium to login the page
    if browser.title == "Login":
        username = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtUsername')
        username.send_keys(settings["USER_NAME"])
        password = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtPassword')
        password.send_keys(settings["PASSWORD"])
        button = browser.find_element_by_name('ctl00$ContentPlaceHolder1$btnLogin')
        button.click()

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return None

    # wait until the page is fully loaded
    try:
        wait.until(lambda driver: driver.find_elements_by_xpath("//span[@class='label_skin_corporation']|//li[@class='copy']"))
    except TimeoutException:
        return None

    title = browser.title
    if title == "Login":
        entry_print("Invalid credential! Please check your login settings.")
        raise CredentialError

    source_code = browser.page_source
    soup = BeautifulSoup(source_code, "html.parser")

    if soup is not None:
        if url.find("televox.west.com") != -1:
            for (name, kwargs) in settings["GET_NEW_SOUP_IGNORE"]:
                for s in soup.find_all(name, **kwargs):
                    s.extract()
        else:
            for (name, kwargs) in settings["GET_OLD_SOUP_IGNORE"]:
                for s in soup.find_all(name, **kwargs):
                    s.extract()

    return soup
