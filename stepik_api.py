import json
import config
import requests
import re


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
    api_url = 'https://stepik.org/api/courses?search={}&page={}'.format(title, page_num)
    course = json.loads(requests.get(api_url, headers={'Authorization': 'Bearer ' + get_token()}).text)
    print(f'course {course}')
    return course


def get_chosen_courses(title):
    i = 1
    page_num = 1
    list_of_choices = []
    has_next_page = True
    pattern = re.compile(r'\b{}\b'.format(re.escape(title)), flags=re.IGNORECASE)
    while has_next_page and i < 3 and page_num <= 15:
        try:
            page_content = get_data(title, page_num)
            courses = page_content['courses']
            for course in courses:
                if ((course['is_active'])
                        and not (course['is_paid'])
                        and (pattern.search(course['title'].lower()))
                        and course['is_popular']
                        and course['learners_count'] >= 500):
                    list_of_choices.append({
                        'course_name': course['title'],
                        'language': course['language'],
                        'url': course['canonical_url']
                    })
                    i += 1
            page_num += 1
            has_next_page = page_content['meta']['has_next']
        except Exception as e:
            print(f"Error exception: something was broken!: {e}")

    return list_of_choices


def main():
    title = 'Redis'
    list_of_choices = get_chosen_courses(title)
    print(f'list_of_choices {list_of_choices}')


main()
