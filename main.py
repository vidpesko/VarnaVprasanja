from .PRIVATE import AVP_PASSWORD, AVP_USERNAME

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm
import json

from time import sleep, time

VEHICLE_URLS = {'A': ['http://teorija-priprava.gov.si/moodle/mod/quiz/view.php?id=41', 15],
                'B': ['http://teorija-priprava.gov.si/moodle/mod/quiz/view.php?id=102', 21]}


def prepare_json():
    with open(json_path, 'w') as j:
        json.dump({}, j)


def backup_data(data_to_add):
    with open(json_path, 'r') as j:
        current_data = j.read()

    try:
        current_data = json.loads(current_data)
    except json.decoder.JSONDecodeError:
        current_data = {}

    current_data.update(data_to_add)

    with open(json_path, 'w') as j:
        json.dump(current_data, j)


def scroll_down(_driver):
    _driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def refresh_page(_driver: webdriver):
    _driver.refresh()


def end_quiz(_driver):
    sleep(1)
    to_click = _driver.find_element(By.CLASS_NAME, "endtestlink")
    to_click.click()
    sleep(3)
    scroll_down(_driver)

    try:
        sleep(1)
        send_test_btn = WebDriverWait(_driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@type='submit' and @value='Oddaj test']")))
        send_test_btn.click()

        try:
            sleep(2)
            popup_to_click = WebDriverWait(_driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="confirmdialog"]/div[3]/span/button[2]')))
            popup_to_click.click()
        except TimeoutException:
            print('Popup not shown')
    except TimeoutException:
        print('Window not shown')


def format_question(html_content):
    return {'html_content': html_content}


def go_to_next_question(_driver):
    # Can you even go to the next question
    can_go = False
    try:
        to_click = _driver.find_element(By.XPATH, '//*[@id="region-main"]/div[2]/div/a')
        btn_text = to_click.get_attribute("title")
        if btn_text == 'Naprej':
            can_go = True
        to_click.click()
        return can_go
    except NoSuchElementException:
        print('Something went wrong')


def start_extracting_quiz(_driver, no_of_questions):
    # First end quiz to get right answers
    end_quiz(_driver)
    sleep(5)
    quiz_id = f'quiz_{str(int(time()))}'
    storage_dict = {quiz_id: []}

    # Extracting all
    show_all_btn = _driver.find_element(By.XPATH, '//*[@id="mod_quiz_navblock"]/div[2]/div[2]/a[1]')
    show_all_btn.click()
    sleep(5)
    for i in range(1, no_of_questions + 1):
        question_id = f'q{i}'
        _driver.execute_script(f'document.getElementById("{question_id}").scrollIntoView();')
        question = _driver.find_element(By.ID, question_id)
        question_html = question.get_attribute('innerHTML')
        question = format_question(question_html)
        storage_dict[quiz_id].append(question)
        sleep(1)

    backup_data(storage_dict)
    sleep(5)
    end_review = _driver.find_element(By.XPATH, '//*[@id="region-main"]/div[2]/div/a')
    end_review.click()
    return 'END'


def start_test(_driver, vehicle):
    should_be_popup = True
    scroll_down(_driver)
    # Click: resi test
    try:
        sleep(2)
        to_click = _driver.find_element(By.XPATH, "//*[@type='submit' and @value='Ponovno reši test']")
        to_click.click()
        # to_click.click()
    except NoSuchElementException:
        try:
            to_click = _driver.find_element(By.XPATH, "//*[@type='submit' and @value='Nadaljujte z zadnjim poskusom']")
            to_click.click()
            should_be_popup = False
            # to_click.click()
        except NoSuchElementException:
            print('Again here')
            # sleep(5)
            # refresh_page(_driver)
            # start_test(_driver, vehicle)
            # print('You have to wait a little bit ~ 50s-60s')
            # return

    # Click on popup
    if should_be_popup:
        try:
            sleep(2)
            popup_to_click = WebDriverWait(_driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="confirmdialog"]/div[3]/span/button[2]')))
            popup_to_click.click()
        except TimeoutException:
            print('Popup not shown')
    sleep(5)
    no_of_questions = VEHICLE_URLS[vehicle][1]
    start_extracting_quiz(_driver, no_of_questions)


def open_started_test(_driver, test):
    pass

    # no_of_questions = VEHICLE_URLS[vehicle][1]
    # start_extracting_quiz(_driver, no_of_questions)


def _login(_driver, elem):
    username_inp = elem.find_element(By.ID, "username")
    password_inp = elem.find_element(By.ID, "password")

    username_inp.clear()
    username_inp.send_keys(AVP_USERNAME)

    password_inp.clear()
    password_inp.send_keys(AVP_PASSWORD)
    password_inp.send_keys(Keys.RETURN)


def login(_driver, elem, vehicle, extract_already_started=False):
    username_inp = elem.find_element(By.ID, "username")
    password_inp = elem.find_element(By.ID, "password")

    username_inp.clear()
    username_inp.send_keys(AVP_USERNAME)

    password_inp.clear()
    password_inp.send_keys(AVP_PASSWORD)
    password_inp.send_keys(Keys.RETURN)

    _driver.get(VEHICLE_URLS[vehicle][0])

    if extract_already_started:
        started_tests = _driver.find_elements(By.CLASS_NAME, 'bestrow')
        for test in started_tests:
            open_started_test(_driver, test)

    for _ in tqdm(range(100)):
        start_test(_driver, vehicle)

        # Wait time
        wait_time = 20 + VEHICLE_URLS[vehicle][1]
        wait_time = (60 - wait_time) + 5
        print(wait_time)

        sleep(wait_time)
        refresh_page(_driver)


if __name__ == '__main__':
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('http://teorija-priprava.gov.si/')

    KATEGORIJA = 'B'

    # Storage information
    json_path = f'ExtractionDatabases/{KATEGORIJA}_kategorija_rawHTML.json'
    json_file = open(json_path, 'a+')

    # Check for login
    try:
        # Login
        myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'login')))

        # prepare_json()
        login(driver, myElem, KATEGORIJA)
    except TimeoutException:
        # No Login
        print('l')
