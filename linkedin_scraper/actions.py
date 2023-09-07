import getpass
from . import constants as c
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import time

solver = TwoCaptcha('c385183e3602ee5515d92f62fa2f5e95')

def __prompt_email_password():
  u = input("Email: ")
  p = getpass.getpass(prompt="Password: ")
  return (u, p)

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

def login(driver, email=None, password=None, cookie = None, timeout=1000):
    if cookie is not None:
        return _login_with_cookie(driver, cookie)

    if not email or not password:
        email, password = __prompt_email_password()

    driver.get("https://www.linkedin.com/login")
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element(By.ID,"username")
    email_elem.send_keys(email)

    password_elem = driver.find_element(By.ID,"password")
    password_elem.send_keys(password)
    password_elem.submit()

    if "https://www.linkedin.com/checkpoint/challenge" in driver.current_url:
        original_window = driver.current_window_handle
        first_main = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        first_iframe = first_main.find_element(By.TAG_NAME,"iframe")
        driver.switch_to.frame(first_iframe)
        second_main = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        second_iframe = second_main.find_element(By.TAG_NAME,"iframe")
        driver.switch_to.frame(second_iframe)
        third_iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(third_iframe)
        fourth_iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        fc_token = driver.find_element(By.ID,"FunCaptcha-Token").get_attribute("value").split('|')
        for item in fc_token:
            if item.startswith("pk="):
                pk = item[3:]
            elif item.startswith("surl="):
                surl = item[5:]
        driver.switch_to.frame(fourth_iframe)
        button = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        button.click()

        # result = solver.funcaptcha(sitekey=pk, url=surl, pageurl=driver.current_url)
        # print(result)

        # driver.switch_to.window(original_window)
        # form = driver.find_element(By.ID,"captcha-challenge")
        # input = form.find_element(By.NAME,"captchaUserResponseToken")
        # driver.execute_script("arguments[0].setAttribute('value', '" + result["code"] + "')", input)
        # form.submit()

    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, c.VERIFY_LOGIN_ID)))

def _login_with_cookie(driver, cookie):
    driver.get("https://www.linkedin.com/login")
    driver.add_cookie({
      "name": "li_at",
      "value": cookie
    })
