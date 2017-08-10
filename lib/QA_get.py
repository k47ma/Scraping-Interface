# coding=utf-8
import string
from config import settings
from QA_error import record_error
from QA_util import check_format, replace_special, entry_print

# modules for getting information from soup


printable = set(string.printable)


# get the address from old site
def get_address_soup_old(soup, url):
    # for different html structures, find the address lines
    if not soup:
        return get_address_soup_new(soup, url)

    address_arr = soup.find_all('p', itemprop="address")
    if not address_arr:
        return get_address_soup_new(soup, url)

    result_arr = []

    for address in address_arr:
        name = address.find('strong', itemprop="name").get_text().replace("|", "").strip()
        if name.endswith(":") or name.endswith("-"):
            name = name[:-1].strip()

        street = address.find('span', itemprop="streetAddress").get_text().replace("|", "").strip()
        city = address.find('span', itemprop="addressLocality").get_text().replace("|", "").strip()
        region = address.find('span', itemprop="addressRegion").get_text().replace("|", "").strip()
        zip = address.find('span', itemprop="postalCode").get_text().replace("|", "").strip()
        phone = address.find('span', itemprop="telephone").get_text().replace("|", "").strip()

        parsed_address = [name, street, city, region + " " + zip, phone]

        for i in range(len(parsed_address)):
            parsed_address[i] = parsed_address[i].upper()

        result_arr.append(parsed_address)
    return result_arr


# get the address from new site
def get_address_soup_new(soup, url):
    file = open("result\\address_detail.txt", 'a')
    # find the address lines
    if not soup:
        record_error(url, "address container")
        return False

    try:
        address_arr = soup.find('p', {'class': "companyname"}).next_sibling.find_all('li')
    except AttributeError:
        record_error(url, "address container")
        address_arr = []
    result_arr = []

    for address in address_arr:
        name = address.find('span', {'class': "locationName"}).get_text().replace("|", "").strip()
        if name.endswith(":") or name.endswith("-"):
            name = name[:-1].strip()

        full_address = address.find('span', {'class': "streetAddress"}).get_text().replace("|", "").strip()
        street_arr = full_address.split(',')
        city = street_arr[-2].replace("|", "").strip()
        zip = street_arr[-1].replace("|", "").strip()

        ind = full_address.rfind(city)
        street = full_address[:ind - 2]

        phone = address.find('span', {'class': "contactNumbers"}).get_text()[6:].replace("|", "").strip()

        if not check_format(full_address):
            entry_print("***********************************************")
            entry_print("ADDRESS FORMAT ISSUE FOUND!")
            entry_print("New URL: " + url)
            entry_print("New address: " + full_address)
            file.write("ADDRESS FORMAT ISSUE FOUND!\n")
            file.write("New URL: " + url + "\n")
            file.write("New address: " + full_address + "\n")
            file.write("-----------------------------------------------\n")

        # if there are fax number or email in the new site, print error and record
        if not address.find('span', {'class': "faxNumbers"}) is None:
            entry_print("***********************************************")
            entry_print("ADDITIONAL FAX NUMBER!")
            entry_print("New URL: " + url)
            entry_print("***********************************************")
            file.write("ADDITIONAL FAX NUMBER!\n")
            file.write("New URL: " + url + "\n")
            file.write("-----------------------------------------------\n")
        if not address.find('span', {'class': "email"}) is None:
            entry_print("***********************************************")
            entry_print("ADDITIONAL EMAIL NUMBER!")
            entry_print("New URL: " + url)
            entry_print("***********************************************")
            file.write("ADDITIONAL EMAIL NUMBER!\n")
            file.write("New URL: " + url + "\n")
            file.write("-----------------------------------------------\n")

        parsed_address = [name, street, city, zip, phone]

        for i in range(len(parsed_address)):
            parsed_address[i] = parsed_address[i].upper()

        result_arr.append(parsed_address)
    file.close()
    return result_arr


# retrieve the metadata from the target site
def get_meta_soup(soup, url):
    # find the title from respond
    try:
        title = soup.title.text.strip().replace("  ", " ")
        title = title.encode('utf-8')
        title = replace_special(title)
    except AttributeError:
        record_error(url, "title")
        title = "none"
    except TypeError:
        record_error(url, "title")
        title = "none"

    # get description from respond
    try:
        description = soup.find("meta", {'name': "description"})
        description = description.get("content").strip().encode('utf-8')
        description = replace_special(description)

        while description.find("  ") != -1:
            description = description.replace("  ", " ")
        if description == "":
            description = "none"
    except TypeError:
        description = "none"
    except AttributeError:
        description = "none"

    # get the keywords from respond
    try:
        keywords = soup.find("meta", {'name': "keywords"})
        keywords = (" ".join(keywords.get('content').strip().splitlines())).encode('utf-8')
        keywords = replace_special(keywords)

        while keywords.find("  ") != -1:
            keywords = keywords.replace("  ", " ")

        if keywords is None:
            keywords = "none"
    except TypeError:
        keywords = "none"
    except AttributeError:
        keywords = "none"

    dic = {'title': title, 'description': description, 'keywords': keywords}
    return dic


# get the content from old page
def get_content_soup_old(soup, url):
    if not soup:
        record_error(url, "content")
        return None

    # remove all the <style> and <script> tags
    if soup:
        for (name, kwargs) in settings["GET_OLD_CONTENT_IGNORE"]:
            for s in soup.find_all(name, **kwargs):
                s.extract()

    content = soup.find('div', class_="right")
    text_list = []

    if content is not None and url.find("form") == -1:
        if content.get_text() == "" or content.get_text().isspace():
            content = soup.find('div', id="content")

    if content is None or content.find('div', id="content"):
        content = soup.find('div', id="content")
    if content is None:
        content = soup.find('div', class_="left")
    if content is None:
        record_error(url, "content container")
        return None

    for child in content.stripped_strings:
        if not child.isspace():
            text_list.append(child.strip())
    # remove special characters and additional spaces
    text = " ".join(text_list)
    text = replace_special(text)
    return text


# get the content from new page
def get_content_soup_new(soup, url):
    if not soup:
        record_error(url, "content container")
        return False

    # remove comment and map from soup
    if soup:
        for (name, kwargs) in settings["GET_NEW_CONTENT_IGNORE"]:
            for s in soup.find_all(name, **kwargs):
                s.extract()

    content = soup.find('div', class_="right")
    text_list = []

    if content is not None and url.find("form") == -1:
        if content.get_text() == "" or content.get_text().isspace():
            content = soup.find('div', id="content")

    if content is None or content.find('div', id="content"):
        content = soup.find('div', id="content")
    if content is None:
        content = soup.find('div', class_="left")
    if content is None:
        record_error(url, "content container")
        return None

    for child in content.stripped_strings:
        if not child.isspace():
            text_list.append(child.strip())
    # remove special characters and additional spaces
    text = " ".join(text_list)
    text = replace_special(text)
    return text


# get the text content for blog page
def get_blog_content(soup):
    # remove all the <style> and <script> tags
    if soup:
        for (name, kwargs) in settings["GET_BLOG_CONTENT_IGNORE"]:
            for s in soup.find_all(name, **kwargs):
                s.extract()

    if soup is None:
        return None

    text_list = []
    for child in soup.stripped_strings:
        if not child.isspace():
            text_list.append(child.strip())

    # remove special characters and additional spaces
    text = " ".join(text_list)
    text = replace_special(text)
    return text


# get the text content for homepage
def get_homepage_content(soup):
    if soup is None:
        return ""
    # remove all the <style> and <script> tags
    if soup:
        for (name, kwargs) in settings["GET_HOMEPAGE_CONTENT_IGNORE"]:
            for s in soup.find_all(name, **kwargs):
                s.extract()

    if soup is None:
        return None

    text_list = []
    for child in soup.stripped_strings:
        if not child.isspace():
            text_list.append(child.strip())

    # remove special characters and additional spaces
    text = " ".join(text_list)
    text = replace_special(text)
    return text
