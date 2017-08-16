from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time


browser = webdriver.Chrome("C:\Users\kma01\Downloads\QA\QA-Interface\chromedriver\chromedriver.exe")
wait = WebDriverWait(browser, 20)
browser.maximize_window()

browser.get("")
username = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtUsername')
username.send_keys("")
password = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtPassword')
password.send_keys("")
submit = browser.find_element_by_name('ctl00$ContentPlaceHolder1$btnLogin')
submit.click()

elements = browser.find_elements_by_xpath("//span[@status='hidden_only']")

for ind in range(len(elements)):
    elements = browser.find_elements_by_xpath("//span[@status='hidden_only']")
    target = elements[ind].find_element_by_tag_name("input")
    target.click()
    time.sleep(1)
