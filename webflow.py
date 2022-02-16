import configparser
import urllib

import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.webdriver import Chrome

parser = configparser.ConfigParser()
parser.read("config.txt")
aws_sso_url = parser.get("web-sso", "aws_sso_url")
principal = parser.get("web-sso", "user")
pwd = parser.get("web-sso", "pwd")
timeout = 25


def do_landing_page() -> Chrome:
    driver = webdriver.Chrome()
    driver.get(url=aws_sso_url)
    return driver


def do_identify_login_page(driver: webdriver) -> int:
    try:
        print("Looking for fresh sign on page element...")
        sso_link = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='loginfmt']"))
        )
        print("Found fresh sign on page element")
        return 1
    except TimeoutException:
        print("Could not find fresh sign on page element. Looking for hint sign on page element...")
        try:
            sso_link = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[@id='tilesHolder']//div[@data-test-id='{principal}']"))
            )
            print("Found hint sign on page element")
            return 2
        except TimeoutException:
            print("Could not find hint sign on page element either. Fatal error.")
            raise Exception("Could not identify the login page type to be handled")


def do_hint_login_page(iter: int, driver: webdriver):
    try:
        hint_link = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[@id='tilesHolder']//div[@data-test-id='{principal}']"))
        )
    except TimeoutException:
        print(f"Could not locate SSO login link on pass #{iter}")
        driver.quit()
        raise Exception("Could not locate SSO login link 1st pass. Exit application.")

    print(f"User SSO link found {hint_link}")
    hint_link.click()


def do_fresh_login_page(driver: webdriver):
        driver.find_element(By.XPATH, "//input[@name='loginfmt']").send_keys(principal)
        driver.find_element(By.XPATH, "//*[@id='idSIButton9']").click()
        print("Input login email on fresh sign on page, proceeding to password page")
        # going to password page
        try:
            pwd_field = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@name='passwd']"))
            )
            print("Found password element to fill in")
            pwd_field.send_keys(pwd)
            driver.find_element(By.XPATH, "//*[@id='idSIButton9']").click()
            print("Submitted password")
        except TimeoutException:
            print("Could not find password element on page. Fatal error.")
            raise Exception("Could not find password element on page")


def do_stay_signed_in_page(driver: webdriver):
    try:
        stay_signed_in = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(string(), 'Stay signed in?')]"))
        )
        print("Stay Signed In page found")
        driver.find_element(By.XPATH, "//*[@id='idSIButton9']").click()
        print("Submitted stay signed in page")
    except TimeoutException:
        print("Could not find Stay signed in page. Ignoring and assuming we have moved on to the AWS landing page.")


def do_saml_response(driver: webdriver) -> str:
    for request in driver.requests:
        if request.response:
            if request.url == "https://signin.aws.amazon.com/saml":
                print("SAML Request found")
                print(f"SAML Request body (url-form-encoded) -> {request.body}")
                body_as_str = request.body.decode("utf-8")
                body = urllib.parse.unquote(body_as_str)
                print(f"SAML Request body decoded {body}")
                if "SAMLResponse" in body:
                    saml_response = body[body.index("=")+1:]
                    print(f"SAMLResponse = {saml_response}")
                    return saml_response


def extract_saml_assertion() -> str:
    chrome = do_landing_page()
    # Sometimes you get a login-hint page and sometimes a completely fresh login page. Need to handle both.
    login_page_type = do_identify_login_page(chrome) # 0 = undefined; 1 = fresh login page; 2 = hint login page
    if login_page_type == 1: # fresh login page
        print("Proceeding to login through a fresh login page")
        do_fresh_login_page(chrome)
    elif login_page_type == 2: # hint login page
        print("Proceeding to login through a hint login page")
        do_hint_login_page(1, chrome)
        do_hint_login_page(2, chrome)
    else:
        raise Exception(f"Unknown login page encountered [{login_page_type}]")
    do_stay_signed_in_page(chrome)
    return do_saml_response(chrome)
