import requests
import json
import database
import time
from collections import Counter
from langdetect import detect
import re

conn = database.create_connection('skillnestbot.db')


def get_list_id_vacancies(search):
    search = search.lower()
    url_list = 'https://api.hh.ru/vacancies'
    list_id = []
    params = {'text': search}
    r = requests.get(url_list, params=params)
    found = json.loads(r.text)['found']
    if not found:
        return [], 0

    if found <= 100:
        params['per_page'] = found
        r = requests.get(url_list, params=params)
        data = json.loads(r.text)['items']
        for vac in data:
            list_id.append(vac['id'])
    else:
        i = 0
        while i <= 1:
            params['per_page'] = 100
            params['page'] = i
            r = requests.get(url_list, params=params)
            if 200 != r.status_code:
                print(f'!ERROR! CODE STATUS: {r.status_code}!')
                break
            data = json.loads(r.text)['items']
            for vac in data:
                list_id.append(vac['id'])
            i += 1

    return list_id, found


def get_data_vacancy(vac_id):
    url_vac = 'https://api.hh.ru/vacancies/%s'
    r = requests.get(url_vac % vac_id)
    data = json.loads(r.text)
    return data


def get_and_store_vacancy(list_id, text_search):
    count = 0
    text_search = text_search.lower()
    for vac_id in list_id:
        data = get_data_vacancy(vac_id)
        print(data)
        print(f'type data: {type(data)}')
        # if data.get('errors', {}).get('value') == 'captcha_required':
        #     return
        vacancy_id = data.get('id')
        vacancy_name = data.get('name')
        area = data.get('area', {}).get('name')
        description = data.get('description')
        lang = detect(description)
        key_skills = [skill['name'].strip() for skill in data.get('key_skills', [])]
        skills = (", ".join((map(str, key_skills))))
        if len(skills) > 1:
            pass
        else:
            skills = None
        if description is None:
            continue

        database.add_vacancy_data(conn, vacancy_id, vacancy_name, area, description, lang, skills, text_search)

        count += 1
        if count % 29 == 0:
            time.sleep(5)


def swap_skills(skills):
    title_mapping = {
        r'\bML\b': 'Машинное обучение',
        r'Machine Learning': 'Машинное обучение',
        r'Data Analysis': 'Анализ данных',
        r'PostgreSQL': 'SQL',
        r'\bMySQL\b': 'SQL',
        r'\bHTML5\b': 'HTML',
        r'\bCSS3\b': 'CSS',
        r'\bREST\b': 'API',
        r'\bFramework\b': '',
        r'\bLLM\b': 'NLP',
        r'\bComputer Vision\b': 'Компьютерное зрение'
    }
    for pattern, replacement in title_mapping.items():
        skills = re.sub(pattern, replacement, skills)

    return skills


def sort_and_count_key_skill(skills_txt):
    skills_list = [skill.strip() for skill in skills_txt.split(",") if skill.strip()]
    skills_counts = Counter(skills_list)
    sorted_skills = sorted(skills_counts.items(), key=lambda x: x[1], reverse=True)

    top_skills_text = '\n'.join([f"{skill} - {count}" for skill, count in sorted_skills[:10]])

    return top_skills_text, sorted_skills[:10]


def check_vacancy_search(conn, text_search):
    text_search = text_search.lower()
    skills = database.get_skills(conn, text_search)
    if not skills:
        list_id, found = get_list_id_vacancies(text_search)
        return list_id, found
    else:
        return skills


def main():
    # skills = database.get_skills(conn, text_search)
    # print(skills)
    # result = check_vacancy_search(conn, text_search)
    # print(type(result))
    # print(result)
    #
    # # Проверяем тип результата
    # if isinstance(result, tuple):
    #     list_id, found = result
    #     print("list_id:", list_id)
    #     print("found:", found)
    # else:
    #     skills = result
    #     print("skills:", skills)


# database.drop_table(conn, 'vacancy_data')
# database.create_vacancy_data_table(conn)
#
    list_id = get_list_id_vacancies(text_search)
    print(list_id)
#
    get_and_store_vacancy(list_id, text_search)
# skills = database.get_skills(conn, text_search)
# skills = ', '.join([str(sk[0]) for sk in skills])
# skills = swap_skills(skills)
# a = conn.cursor()
# a.execute("SELECT description FROM vacancy_data WHERE text_search = ?", (text_search,))
# description = a.fetchall()
# a.close()
# descriptions = ' '.join([str(desc[0]) for desc in description])
# print(type(descriptions))
# print(descriptions)
#
# skills_list_top = sort_and_count_key_skill(skills)
# print(f' skills_list_top {skills_list_top}')
#
# print(f'Вот ТОП 10 самых часто встречающихся навыков:')
# for skill, count in skills_list_top[:10]:
#     print(f"{skill} - {count}")


text_search = 'Java'
# main()
