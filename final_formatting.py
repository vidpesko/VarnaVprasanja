import os

from main import _login

import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

from tqdm import tqdm
import requests
import json
from bs4 import BeautifulSoup
import time

AVP_USERNAME = 'janez_novak_ne_mara_avp'
AVP_PASSWORD = 'PofukaniAVP123'

f = open('database.json')
json_obj = json.loads(f.read())


# Needed formatting:
# -remove duplicate questions: store all the questions together, and then use -> mylist = list(dict.fromkeys(mylist)) <-
def get_all_questions(j_obj):
    _questions = []
    for quiz_name, quiz_questions in j_obj.items():
        quiz_questions = [q['html_content'] for q in quiz_questions]
        _questions.extend(quiz_questions)
    return _questions


def remove_duplicates(_questions):
    return list(dict.fromkeys(_questions))


def remove_duplicate_dict(_questions):
    all_dicts = {}
    for q in _questions:
        q_id = q['id']

        question = q["content"]["questions_text"]
        answers = q['content']['answers']
        answers.sort(key=lambda x: len(x))
        answers = '/'.join(answers)

        dict_id = question + answers

        try:
            all_dicts[dict_id].append(q_id)
        except KeyError:
            all_dicts[dict_id] = [q_id, ]

    # all_dicts = remove_duplicates(all_dicts)
    values = all_dicts.values()
    new_questions = []
    times_repeated = []
    for val in values:
        times_repeated.append((len(val), val[0]))
        val = val[0]
        single_q = None
        for q in _questions:
            if q['id'] == val:
                single_q = q
                break
        new_questions.append(single_q)

    times_repeated.sort(key=lambda x: x[0])
    print(times_repeated)

    return new_questions

    # _questions = []
    # for q in all_dicts:
    #     q = q.split('/')
    #     # 0:
    #
    #     _questions.append()


def get_all_image_links(_questions):
    links = []
    for q in _questions:
        # Get image (if there is none return [] )
        image = q['content']['image_link']
        if image[:4] == 'http':
            links.append(image)

    return links


def generate_path_name(_url):
    image_url = _url.split('/')[-4:]
    path_name = '_'.join(image_url)
    return path_name.replace('.', '+')


def execute_save_image_as(_path_name, first_run=True):
    # screenWidth, screenHeight = pyautogui.size()
    pyautogui.press(['down', 'down', 'enter'])
    time.sleep(1)
    pyautogui.write(_path_name)
    if first_run:
        pyautogui.click(x=442, y=656)
    pyautogui.press('enter')


def download_img(link, _driver, is_logged_in, first_img=True):
    try:
        _driver.get(link)
    except TimeoutException:
        print('Timeout reached:', link)
        return {link: 'TIMEOUT'}

    if not is_logged_in:
        elem = WebDriverWait(_driver, 5).until(EC.presence_of_element_located((By.ID, 'login')))
        _login(_driver, elem)

    image = _driver.find_element(By.TAG_NAME, 'img')
    image_url = image.get_attribute('src')
    actionChains = ActionChains(_driver)
    actionChains.context_click(image).perform()

    # Generating path name
    path_name = generate_path_name(image_url)
    execute_save_image_as(path_name, first_run=first_img)
    return {link: path_name}


def download_images(links, _driver):
    _images_names = {}
    is_logged_in = False
    for link in tqdm(links):
        # Checking if file exists
        path_name = os.getcwd() + 'Display/static/Images/QuestionImages/' + generate_path_name(link)
        exists = os.path.exists(path_name)
        if not exists:
            to_update = download_img(link, _driver, is_logged_in, first_img=not is_logged_in)
            _images_names.update(to_update)
            is_logged_in = True

    print(_images_names)
    return _images_names


def final_format(_questions):
    formatted_questions = []
    # {
    #     "id": 1010
    #     "info": {
    #         "points": 4
    #     },
    #     "content": {
    #         "question_text": "Hello, what is 1 + 1",
    #         "image_link": "htpps:lfle///",
    #         "type": "radio/checkbox/custom_input",
    #         "answers": [
    #             "2",
    #             "3",
    #             "6"
    #         ],
    #         "right_answers": [
    #             0,
    #             2
    #         ]
    #     }
    # }
    # }
    for index, q in enumerate(_questions):
        q_id = str(index).zfill(4)

        q = BeautifulSoup(q, 'html.parser')
        # print(q.prettify())

        # Get grade
        grade = q.find_all('div', {'class': 'grade'})[0]
        grade = int(grade.text.strip()[-4:-3])

        # Get Content
        # Get question
        question_text_full = q.find_all('div', {'class': 'qtext'})[0]
        question_text = question_text_full.text.strip()

        # Get image (if there is none return [] )
        image = question_text_full.find_all('img')
        if image:
            image = image[0]['src']
        else:
            image = ""

        # Get answers and answer type
        answers_div = q.find('div', {'class': 'answer'})
        answers_html = answers_div.find_all('div')
        answer_type = answers_html[0].input['type']
        answers = []
        right_answers_indexes = []
        for i, answer in enumerate(answers_html):
            answer_text = answer.text.strip()
            answers.append(answer_text)
            if answer_type == 'checkbox':
                is_correct = answer.img['alt']
                if is_correct == 'Pravilno':
                    right_answers_indexes.append(i)

        # Get right answers
        right_answer = q.find('div', {'class': 'rightanswer'})
        right_answer_full = right_answer.text.strip()
        right_answer_response = right_answer_full.replace('Pravilen odgovor je:', '').strip()

        if not right_answers_indexes:
            right_answers_indexes = [answers.index(right_answer_response)]

        return_format = {
            "id": q_id,
            "info": {
                "points": grade
            },
            "content": {
                "questions_text": question_text,
                "image_link": image,
                "type": answer_type,
                "answers": answers,
                "right_answers": right_answers_indexes,
                "right_answer_response": right_answer_response
            }
        }

        formatted_questions.append(return_format)

    return formatted_questions


def save_questions(_questions):
    _questions = {'questions': _questions}
    with open(os.getcwd() + '/Display/Temporary/questions.json', 'w') as j:
        json.dump(_questions, j)


def save_images_names(_names):
    # names_path = os.getcwd() + '/Display/Temporary/questions.json'
    _questions = {'images_names': _names}
    with open('images_names.json', 'w') as j:
        json.dump(_questions, j)


def join_image_names_with_questions(questions, names):
    images_urls = names.keys()
    for q in questions:
        if q['content']['image_link'] in images_urls:
            new_name = names[q['content']['image_link']].split('+')
            extension = new_name[-1]
            new_name = '+'.join(new_name) + f'.{extension}'

            q['content']['image_link'] = new_name
            # print(q['content']['image_link'])
    return questions


def final_formatting_function(_driver):
    print('Opening database.json')
    # old_questions = open('Display/Temporary/questions.json.json')
    # old_questions = json.load(old_questions)['questions']
    _questions = get_all_questions(json_obj)
    print('Formatting questions into final format')
    _questions = final_format(_questions)

    print('Adding previously downloaded images')
    with open('Display/Temporary/images_names.json') as names:
        _questions = join_image_names_with_questions(_questions, json.load(names)['images_names'])

    print('Removing duplicates')
    _questions = remove_duplicate_dict(_questions)

    print('Getting all image links')
    images_links = get_all_image_links(_questions)
    print('Starting download of images')
    images_names = download_images(images_links, _driver)
    print('Downloading ended')

    print('Updating old question image links with new one')
    _questions = join_image_names_with_questions(_questions, images_names)

    save_questions(_questions)



# service = Service()
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(service=service, options=options)
# driver.set_page_load_timeout(10)

questions = get_all_questions(json_obj)
print(len(questions))
questions = final_format(questions)
print(len(questions))
questions = remove_duplicate_dict(questions)
print(len(questions))
#
# questions = final_format(questions)

# questions = open(os.getcwd() + '/Display/Temporary/questions.json')
# questions = json.load(questions)['questions']
# print(len(questions))
#
# print(len(remove_duplicate_dict(questions)))

# final_formatting_function(driver)

# images_links = get_all_image_links(questions)
# images_names = download_images(images_links, _driver)
# save_images_names(images_names)


# with open('Display/Temporary/images_names.json') as names:
#     questions = final_format(questions)
#     questions = join_image_names_with_questions(questions, json.load(names)['images_names'])
#
#     save_questions(questions)
#