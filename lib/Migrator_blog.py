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
from config import settings
from QA_util import entry_print

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
            parsed_post['summary'] = summary
        else:
            parsed_post['summary'] = None

        parsed_posts.append(parsed_post)

    return parsed_posts


# get article from old blog post
def get_article(old_post):
    source_code = requests.get(old_post)
    text = source_code.text
    soup = BeautifulSoup(text, "html.parser")

    article = soup.find('article')
    header = article.find('header')
    header.extract()

    bad_images = soup.find_all('img', src=re.compile("^data:"))
    for image in bad_images:
        image['src'] = ""

    text = unicode(article)
    text = text.replace("’", "'").replace("“", "\"").replace("”", "\"")

    return text


# migrate post from old site
def migrate_post(old_post, new_blog, browser):
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

    content_space_page = browser.find_element_by_xpath(
        '//li[@class="optionAddPage"]//ul//li/a[text()="News/Blog Content Page"]')
    content_space_page.click()

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
    browser = webdriver.Chrome(executable_path=settings["EXECUTABLE_PATH"])
    browser.maximize_window()

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.01)

    blog_posts = get_blog_posts(old_blog)

    if progress_var:
        progress_var.set(progress_var.get() + step * 0.02)

    step *= 0.97

    if not blog_posts:
        entry_print("Unable to get blog posts for " + old_blog)
        browser.quit()
        return

    blog_step = step / len(blog_posts)

    for post in blog_posts:
        migrate_post(post, new_blog, browser)
        entry_print('\"' + post['title'][0] + "\" migrated!")
        if progress_var:
            progress_var.set(progress_var.get() + blog_step)
    browser.close()


# remove duplicate "-" in post names
def refine_name(name):
    while name.find("--") != -1:
        name = name.replace("--", "-")
    name = name.strip("-")
    return name
