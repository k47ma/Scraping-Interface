# coding=utf-8
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Migrator_util import login
from config import *
from QA_util import migration_print, get_domain

# module for migrating blog pages


# get all old post information in a parsed list
def get_blog_posts(old_blog):
    source_code = requests.get(old_blog)
    text = source_code.text
    soup = BeautifulSoup(text, "html.parser")

    parsed_posts = []
    blog_posts_container = soup.find('ul', class_="content-list")
    blog_posts = blog_posts_container.find_all('li')

    titles = []

    for post in blog_posts:
        parsed_post = {}

        url = post.find(['h3', 'h5']).a['href']
        parsed_post['url'] = url

        title = post.find(['h3', 'h5']).a.get_text()
        parsed_title = (title, 0)
        while parsed_title in titles:
            parsed_title = (title, parsed_title[1]+1)
        titles.append(parsed_title)
        parsed_post['title'] = parsed_title

        date_container = post.find('p', class_="info")
        date = list(date_container.stripped_strings)[0]
        parsed_post['date'] = date.replace('|', '').strip()

        summary_container = post.find('p', class_=False)
        if summary_container:
            summary = summary_container.get_text()
            parsed_post['summary'] = summary.strip()
        else:
            parsed_post['summary'] = None

        parsed_posts.append(parsed_post)

    return parsed_posts


# get article from old blog post
def get_article(old_post):
    source_code = requests.get(old_post)
    text = source_code.text
    soup = BeautifulSoup(text, "html.parser")

    domain = get_domain(old_post)
    if not domain:
        domain = ""

    article = soup.find('article')
    header = article.find('header')
    header.extract()

    bad_images = soup.find_all('img', src=re.compile("^data:"))
    for image in bad_images:
        image['src'] = ""

    # change link to friendly url
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        link['href'] = href.replace("http://www." + domain + ".com", "").replace("http://www." + domain + ".ca", "").replace("http://www." + domain + ".televox.iapps.com", "")

    text = unicode(article)
    text = text.replace("’", "'").replace("“", "\"").replace("”", "\"").strip()

    return text


# migrate post from old site
def migrate_post(old_post, new_blog, browser):
    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    wait = WebDriverWait(browser, 20)
    browser.get(new_blog)

    if browser.title == "Login":
        login(browser, wait)

    new_soup = BeautifulSoup(browser.page_source, "html.parser")
    login_status = new_soup.find('a', id="ctl00_lnkGateway").get_text()
    if login_status == "Login":
        login_button = browser.find_element_by_id("ctl00_lnkGateway")
        login_button.click()
        wait.until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtUsername")))
        login(browser, wait)

    page_option = browser.find_element_by_xpath("//li[@class='optionAddPage']")
    page_option.click()

    try:
        content_space_page = browser.find_element_by_xpath(
            '//li[@class="optionAddPage"]//ul//li/a[text()="News/Blog Content Page"]')
        content_space_page.click()
    except NoSuchElementException:
        migration_print("Can't find + News/Blog Content Page button. Please make sure Our Blog is a News/Blog Page.")

    try:
        title_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl06_txtTitle']")
    except NoSuchElementException:
        title_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl01_txtTitle']")
    title_entry.send_keys(old_post['title'][0])
    if old_post['title'][1]:
        title_entry.send_keys(str(old_post['title'][1]))

    generate_name = browser.find_element_by_xpath("//img[@title='Generate Name']")
    generate_name.click()

    try:
        name_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl06_txtCanonicalName']")
    except NoSuchElementException:
        name_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl01_txtCanonicalName']")
    name = refine_name(name_entry.get_attribute("value")[:50])
    if old_post['title'][1] and not name.endswith(str(old_post['title'][1])):
        name = refine_name(name_entry.get_attribute("value")[:49] + str(old_post['title'][1]))
    name_entry.clear()
    name_entry.send_keys(name)

    try:
        create_page = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl06_btnSubmit']")
    except NoSuchElementException:
        create_page = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl01_btnSubmit']")
    create_page.click()

    try:
        title_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl07_ctl48_field_title']")
    except NoSuchElementException:
        try:
            title_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl02_ctl48_field_title']")
        except NoSuchElementException:
            return
    title_entry.send_keys(old_post['title'][0])

    if old_post['summary']:
        try:
            summary_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl07_ctl48_field_summary']")
        except NoSuchElementException:
            summary_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl02_ctl48_field_summary']")
        summary_entry.send_keys(old_post['summary'])

    try:
        date_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl07_ctl48_field_published_date_dateInput']")
    except NoSuchElementException:
        date_entry = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl02_ctl48_field_published_date_dateInput']")
    date_entry.send_keys(old_post['date'])

    remode_html = browser.find_element_by_xpath("//a[@class='reMode_html']")
    remode_html.click()

    article = get_article(old_post['url'])
    try:
        browser.switch_to.frame(browser.find_element_by_xpath("//td[@id='ctl00_ContentPlaceHolder1_ctl07_ctl48_field_body_ctl00Center']//iframe[2]"))
    except NoSuchElementException:
        browser.switch_to.frame(browser.find_element_by_xpath("//td[@id='ctl00_ContentPlaceHolder1_ctl02_ctl48_field_body_ctl00Center']//iframe[2]"))
    content_entry = browser.find_element_by_xpath("//textarea")
    content_entry.click()
    content_entry.send_keys(article)
    browser.switch_to.default_content()

    try:
        publish = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl07_ibPublishBottom']")
    except NoSuchElementException:
        publish = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl02_ibPublishBottom']")
    publish.click()

    try:
        publish2 = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl07_ibPublishTop']")
    except NoSuchElementException:
        publish2 = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl02_ibPublishTop']")
    publish2.click()

    try:
        yes = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl07_btnYes']")
    except NoSuchElementException:
        yes = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_ctl02_btnYes']")
    yes.click()


# migrate all blog pages under blog
def migrate_blog(old_blog, new_blog, progress_var=None, step=100.0):
    old_url = old_blog.strip()
    new_url = new_blog.strip()

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

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

    # check program status
    if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
        return

    # create new webdriver
    browser = webdriver.Chrome(executable_path=settings["EXECUTABLE_PATH"])
    browser.maximize_window()

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.01)

    blog_posts = get_blog_posts(old_url)

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.02)

    step *= 0.95

    if not blog_posts:
        migration_print("Unable to get blog posts for " + old_url)
        browser.quit()
        return

    blog_step = step / len(blog_posts)

    for post in blog_posts:
        # check program status
        if status["INTERFACE_MODE"] and not status["CHECKING_STATUS"]:
            return

        migrate_post(post, new_url, browser)

        migration_print('\"' + post['title'][0] + "\" migrated!")
        if progress_var:
            progress_var.set(progress_var.get() + blog_step)

    set_status(new_blog, browser)
    if progress_var:
        progress_var.set(progress_var.get() + step * 0.02)

    browser.close()


# set all page status to be "hide selection"
def set_status(new_blog, browser):
    wait = WebDriverWait(browser, 20)
    browser.get(new_blog)

    if browser.title == "Login":
        login(browser, wait)

    option = browser.find_element_by_xpath("//li[@class='optionPageOptions']")
    option.click()

    # get relative path from a tag
    page_status = browser.find_element_by_xpath("//li[@class='optionPageOptions']//ul//li/a[text()='Page Status']")
    href = page_status.get_attribute('href')

    rel_url = re.search("/cms/.*PtlPageSubPages", href).group(0)
    main_url = re.match(".*\.televox\.west\.com", new_blog).group(0)

    browser.get(main_url + rel_url)

    elements = browser.find_elements_by_xpath("//span[@status='hidden_only']")

    for ind in range(len(elements)):
        elements = browser.find_elements_by_xpath("//span[@status='hidden_only']")
        target = elements[ind].find_element_by_tag_name("input")
        target.click()


# remove duplicate "-" in post names
def refine_name(name):
    while name.find("--") != -1:
        name = name.replace("--", "-")
    name = name.strip("-")
    return name
