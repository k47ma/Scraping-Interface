from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

USER_NAME = ""
PASSWORD = ""

browser = webdriver.Chrome("C:\Users\kma01\Downloads\QA\QA-Interface\chromedriver\chromedriver.exe")
browser.maximize_window()
wait = WebDriverWait(browser, 20)
file = open("url.csv", 'w')

browser.get("https://westdesign.teamwork.com/#milestones/274134")

username = browser.find_element_by_id("nameoremail")
username.send_keys(USER_NAME)

password = browser.find_element_by_id("passwordfield")
password.send_keys(PASSWORD)

login = browser.find_element_by_xpath("//input[@value='Login']")
login.click()

wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "msTaskLists")))

task_list = browser.find_element_by_class_name("msTaskLists")
tasks = task_list.find_elements_by_tag_name("li")

for task in tasks:
    task_link = task.find_element_by_tag_name("a")

    text = task_link.get_attribute("innerHTML")
    soup = BeautifulSoup(text, "html.parser")
    file.write(soup.get_text().strip().replace(",", "") + ",")

    task_link.click()

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "description")))

    description = browser.find_element_by_xpath("//div[@class='description']//p/..")
    text = description.get_attribute("innerHTML")

    soup = BeautifulSoup(text, "html.parser")

    ind = 0
    for link in soup.stripped_strings:
        if ind == 1:
            file.write(link + ",")
        elif ind == 2:
            file.write(link + "\n")
        ind += 1

    close = browser.find_element_by_xpath("//div[@class='header-close']")
    close.click()

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "msTaskLists")))

browser.close()
