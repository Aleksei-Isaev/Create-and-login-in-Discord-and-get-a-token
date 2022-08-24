import os
import time
import random
import requests

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def logout(driver):
    print("Logout in process, just wait...")

    driver.execute_script(
        "setInterval(()=>{document.body.appendChild("
        "document.createElement`iframe`).contentWindow.localStorage.token=null},50),setTimeout(()=>{location.reload("
        ")},0);"
    )

    time.sleep(2)

    driver.delete_all_cookies()


def get_email():
    email = input("Enter email: ")

    while True:
        if len(email) > 2:
            if "@gmail.com" and "@" not in email:
                email += "@gmail.com"
            break

        else:
            email = input("Enter correct email: ")

    return email


def get_username():
    username = input("Enter your username: ")

    while True:
        if len(username) > 2:
            break

        else:
            username = input("Enter correct username: ")

    return username


def captcha_solver():
    print("Solving captcha, just wait...")

    api_key = os.environ["API_KEY"]
    site_key = "4c672d35-0701-42b2-88c3-78380b0db560"
    url = "https://discord.com/register"
    captcha_request = f"https://2captcha.com/in.php?key={api_key}&method=hcaptcha&sitekey={site_key}&pageurl={url}"

    while True:
        request = requests.get(captcha_request)
        text = request.text
        get_id = text[3:]

        time.sleep(24)

        response_of_token = f"https://2captcha.com/res.php?key={api_key}&action=get&id={get_id}"
        answer_of_captcha = requests.get(response_of_token)

        if answer_of_captcha.text[3:] == "CHA_NOT_READY":
            print("Captcha is not ready, just wait...")
            continue

        else:
            break

    return answer_of_captcha.text[3:]


def register_user():
    alphabet_and_numbers = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    password = "".join(random.choices(alphabet_and_numbers, k=8))
    email = get_email()
    username = get_username()
    day = int(random.randint(1, 28))
    months = [
        "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
        "December"
    ]

    month = random.choice(months)
    year = int(random.randint(1902, 2004))

    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get("https://discord.com/register")

    elements = driver.find_elements_by_tag_name("input")
    keys = (email, username, password, day, month + "\ue004", year)

    for text, element in zip(keys, elements):
        element.send_keys(text)

        time.sleep(0.05)

    try:
        driver.find_element_by_css_selector('input[type="checkbox"]').click()

        while True:
            driver.find_elements_by_tag_name("button")[0].click()

            try:
                driver.find_element_by_class_name("errorMessage-38vAlK")
                print("You have got ban... Just wait a minute and try again.")

                time.sleep(60)
                continue

            except Exception:
                break

    except Exception as expt:
        print(expt)

    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, '//iframe[@id="hcaptcha-iframe"]'))
        )
    except Exception as expt:
        print(expt)

    try:

        captcha = captcha_solver()

        driver.execute_script(
            f"document.querySelector('iframe').parentElement.parentElement.__reactProps$.children"
            f".props.onVerify('{captcha}')"
        )

    except Exception as expt:
        print(expt)

    try:
        WebDriverWait(driver, 20).until(
            lambda driver_url: driver.current_url != "https://discord.com/register"
        )

        token = driver.execute_script(
            'location.reload();var i=document.createElement("iframe");document.body.appendChild(i);return '
            "i.contentWindow.localStorage.token"
        ).strip('"')

        print('{"token": "' + token + '"}')

    except TimeoutException:
        print("You have some problem...")

        pass

    else:
        print("Done!")

    finally:
        logout(driver)

    driver.quit()


if __name__ == "__main__":
    register_user()
