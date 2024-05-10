import json
import config
import requests
import re

import database

conn = database.create_connection('skillnestbot.db')

database.create_course_data_table(conn)


# database.drop_table(conn, 'stepik_courses')


def get_token():
    client_id = config.stepik_client_id
    client_secret = config.stepik_client_secret

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    resp = requests.post('https://stepik.org/oauth2/token/',
                         data={'grant_type': 'client_credentials'},
                         auth=auth)
    token = json.loads(resp.text)['access_token']
    print(f'token {token}')
    return token


def get_data(title, page_num):
    api_url = 'https://stepik.org/api/courses?search={}&page={}&language=ru&is_paid=False&is_certificate_with_score=True&is_popular=True'.format(
        title, page_num)
    course = json.loads(requests.get(api_url, headers={'Authorization': 'Bearer ' + get_token()}).text)
    print(f'course {course}')
    return course


def get_chosen_courses(title):
    i = 1
    page_num = 1
    has_next_page = True
    pattern = re.compile(r'\b{}\b'.format(re.escape(title)), flags=re.IGNORECASE)
    print(f'pattern {pattern}')
    while has_next_page and i < 3 and page_num <= 15:
        try:
            page_content = get_data(title, page_num)
            courses = page_content['courses']
            for course in courses:
                if ((course['is_active']) and (pattern.search(course['title'].lower())) and course[
                    'learners_count'] >= 1000) \
                        and i <= 3:
                    course_id = course.get('id')
                    name = course.get('title')
                    url = course.get('canonical_url')
                    database.add_course_data(conn, course_id, name, url, title)
                    i += 1
            page_num += 1
            has_next_page = page_content['meta']['has_next']
        except Exception as e:
            print(f"Error exception: something was broken!: {e}")


def get_courses(conn, title):
    list_of_course = database.get_course_info(conn, title)
    if not list_of_course:
        get_chosen_courses(title)
        list_of_course = database.get_course_info(conn, title)

    return list_of_course


def message_with_courses(list_of_courses):
    message = "Вот подборка курсов по навыку Анализ данных:\n\n"
    for course in list_of_courses:
        name = course[2]
        url = course[3]
        message += f"\- [{name}]({url})\n"
    return message


def main():
    title = 'c++'
    list_of_course = get_courses(conn, title)
    for course in list_of_course:
        name = course[2]
        url = course[3]
        print(f'name: {name}\nurl: {url}')


# main()
