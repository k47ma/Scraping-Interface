from requests import get
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import csv
from ThreadPool import ThreadPool

# module for determining the site type


HORIZONTAL = 1
VERTICAL = 2


def site_type(soup):
    template = soup.find('div', id="template")
    try:
        template_class = template.get('class')
    except AttributeError:
        return None
    template_class = " ".join(template_class)
    if template_class.find("h_left") != -1 or template_class.find("h_center") != -1 \
            or template_class.find("essential") != -1:
        return HORIZONTAL
    elif template_class.find("vertical") != -1:
        return VERTICAL


def get_soup(url):
    source = get(url)
    plain_text = source.text
    soup = BeautifulSoup(plain_text, "html.parser")

    title = soup.find('title').get_text().strip()
    if title == "Login":
        return None
    elif title == "Home | Root | Seattle Washington":
        return -1
    else:
        return soup


def test():
    file = open("C:\Users\kma01\Downloads\essentials.csv", 'r')
    rows = csv.reader(file)
    threadpool = ThreadPool(10)

    for row in rows:
        layout = row[0].strip().lower()
        old_url = row[1]
        new_url = "http://" + old_url.split('.')[0] + ".televox.west.com"

        threadpool.add_task(check_site, layout, new_url)
    threadpool.wait_completion()


def check_site(layout, new_url):
    try:
        new_soup = get_soup(new_url)
    except ConnectionError:
        return

    if new_soup is None:
        return

    if new_soup == -1:
        return

    new_type = site_type(new_soup)
    if new_type == HORIZONTAL:
        if layout.find("horizontal") != -1:
            result = True
    elif new_type == VERTICAL:
        if layout.find("vertical") != -1 or layout.find("verticle") != -1:
            result = True
    else:
        print "Unable to find the site type for " + new_url
        result = False

    if result:
        print new_url + " PASSED!"
    else:
        print new_url, new_type, layout

test()
