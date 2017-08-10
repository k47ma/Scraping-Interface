# coding=utf-8
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from config import settings

# module for helper functions in migration


# ask the user to continue
def ask_continue():
    cmd = ""
    while cmd.lower() != 'y':
        cmd = raw_input("Please enter y to continue: ")
    print("-----------------------------------------------------------")


# login to the site
def login(browser, wait):
    if browser.title == "Login":
        username = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtUsername')
        username.send_keys(settings["USER_NAME"])
        password = browser.find_element_by_id('ctl00_ContentPlaceHolder1_txtPassword')
        password.send_keys(settings["PASSWORD"])
        submit = browser.find_element_by_name('ctl00$ContentPlaceHolder1$btnLogin')
        submit.click()
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_lblCompany")))
