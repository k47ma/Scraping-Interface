import requests
from urlparse import urlparse
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains


def get_content_old(old_url):
    source_code = requests.get(old_url)
    text = source_code.text
    old_soup = BeautifulSoup(text, "html.parser")

    old_contents = old_soup.find_all('div', class_="iapps-container-container")

    result = []

    for old_contnet in old_contents:
        result.append(unicode(str(old_contnet), errors="ignore"))

    return result


# migrate content from old page to new page
def migrate_content(old_url, new_url, browser, name, parent_name):
    rel_url = urlparse(new_url).path
    old_contents = get_content_old(old_url)

    actions = ActionChains(browser)

    if not old_contents:
        print("Nothing to migrate from " + old_url)
        return

    ind = 1
    for old_content in old_contents:
        browser.get(new_url + "?action=design")
        login(browser)

        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[@src='/common/resources/Portlet/web-content.png']")))

        actions.move_to_element(browser.find_element_by_class_name("portlet_zone")).perform()
        actions.drag_and_drop(browser.find_element_by_xpath("//img[@src='/common/resources/Portlet/web-content.png']"),
                              browser.find_element_by_class_name("portlet_zone")).perform()

        wait.until(EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_txtTitle')))
        title_entry = browser.find_element_by_id("ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_txtTitle")

        if len(old_contents) == 1:
            title_entry.send_keys(name)
        else:
            title_entry.send_keys(name + str(ind))
            ind += 1

        remode = browser.find_element_by_class_name("reMode_html")
        remode.click()

        content_entry = browser.find_element_by_id("ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_reEditArea_ctl00_contentIframe")
        content_entry.send_keys(old_content)

        save = browser.find_element_by_id("ctl00_ContentPlaceHolder1_ctl07_ctl46_ctl00_ibTelevoxSaveAsBottom")
        save_href = save.get_attribute("onclick")
        save_url = re.search("http://.*location=local", save_href).group(0)

        browser.get(save_url)

        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "TM-plus")))

        expand_lib = browser.find_element_by_class_name("TM-plus")
        expand_lib.click()

        folder = browser.find_element_by_xpath("//a[@class='TM-subfolder']/span/text()[.='" + parent_name + "']")

        if folder:
            folder.click()
        else:
            main_folder = browser.find_element_by_class_name("TM-mainFolder")
            main_folder.click()
            new_folder = browser.find_element_by_id("btnNewFolder")
            new_folder.click()
            folder_name = browser.find_element_by_class_name("swal2-input")
            folder_name.send_keys(rel_url.split('/')[1])
            confirm = browser.find_element_by_class_name("swal2-confirm")
            confirm.click()

        save = browser.find_element_by_id("btnSave")
        save.click()

