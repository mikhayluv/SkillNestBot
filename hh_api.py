import requests
import json
import database
import time
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import threading

conn = database.create_connection('skillnestbot.db')


def get_list_id_vacancies(text):
    url_list = 'https://api.hh.ru/vacancies'
    list_id = []
    params = {'text': text}
    r = requests.get(url_list, params=params)
    found = json.loads(r.text)['found']
    if found:
        print(f'По вашему запросу: "{text}" было найдено {found} вакансий!')
    else:
        print(f'По вашему запросу: "{text}" не было найдено вакансий :( \n Проверьте введенные данные!!!')

    if found <= 100:
        params['per_page'] = found
        r = requests.get(url_list, params=params)
        data = json.loads(r.text)['items']
        for vac in data:
            list_id.append(vac['id'])
    else:
        print(f'Для более быстрого анализа я просканирую 200 самых новых вакансий!')
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

    return list_id


def get_data_vacancy(id):
    url_vac = 'https://api.hh.ru/vacancies/%s'
    r = requests.get(url_vac % id)
    data = json.loads(r.text)
    return data


def get_salary(data):
    if data.get('salary') is None:
        return {"currency": None, 'from': None, 'to': None, 'gross': None}
    else:
        salary_data = {'currency': data['salary'].get('currency'),
                       'from': data['salary'].get('from'),
                       'to': data['salary'].get('to'),
                       'gross': data['salary'].get('gross')}
        return salary_data


def get_and_store_vacancy(list_id):
    count = 0

    for vac_id in list_id:
        data = get_data_vacancy(vac_id)
        vacancy_id = data.get('id')
        vacancy_name = data.get('name')
        area = data.get('area', {}).get('name')
        salary_data = get_salary(data)
        salary_from = salary_data.get('from')
        salary_to = salary_data.get('to')
        currency = salary_data.get('currency')
        description = data.get('description')

        database.add_vacancy_data(conn, vacancy_id, vacancy_name, area, salary_from, salary_to, currency, description)

        # print(f'iteration: {count}')
        # print(f'vacancy_id: {vacancy_id}')
        # print(f'vacancy_name: {vacancy_name}')

        count += 1
        if count % 29 == 0:
            time.sleep(5)

    print(f"STORE VACANCY IS DONE!")


def get_and_store_key_skills(list_id):
    all_skills = []
    skills_txt = ''
    for vac_id in list_id:
        data = get_data_vacancy(vac_id)
        vacancy_id = data.get('id')
        vacancy_name = data.get('name')
        key_skills = [skill['name'].strip() for skill in data.get('key_skills', [])]
        skills = (", ".join((map(str, key_skills))))
        if key_skills:
            all_skills.append(skills)
            skills_txt += f'{skills}, '
            database.add_keys_kills_data(conn, vacancy_id, vacancy_name, skills)
        else:
            continue
    skills_txt = skills_txt[:-2]
    print(f"STORE SKILLS IS DONE!")
    return all_skills, skills_txt


def sort_and_count_key_skill(skills_txt):
    skills_list = [skill.strip() for skill in skills_txt.split(",")]

    skills_counts = Counter(skills_list)
    sorted_skills = sorted(skills_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_skills


def run_threads(list_id):
    result = []

    thread_vacancy = threading.Thread(target=get_and_store_vacancy, args=[list_id])

    def thread_key_skills():
        all_skills, skills_txt = get_and_store_key_skills(list_id)
        print(f'all_skills from thread key skills {all_skills}')
        print(f'skills_txt from thread key skills {skills_txt}')
        result.append(skills_txt)

    thread_key_skills = threading.Thread(target=thread_key_skills)

    thread_vacancy.start()
    thread_key_skills.start()

    thread_vacancy.join()
    thread_key_skills.join()

    skills = (", ".join((map(str, result))))
    print("Results:", skills)

    return skills


def draw_pie_scatter(text_search, skill_list):
    data = [count for skill, count in skill_list[:10]]
    labels = [skill for skill, count in skill_list[:10]]

    colors = sns.color_palette('pastel')[:len(data)]

    plt.figure(figsize=(10, 8))
    plt.pie(data, labels=labels, colors=colors, autopct='%.0f%%')
    plt.title(f'Доли навыков по запросу: {text_search}')
    plt.show()


def main():

    database.drop_table(conn, 'vacancy_data')
    database.create_vacancy_data_table(conn)

    database.drop_table(conn, 'key_skills_data')
    database.create_keys_kills_data_table(conn)

    text_search = 'Data Science Junior'
    list_id = get_list_id_vacancies(text_search)

    skills_txt = run_threads(list_id)

    skills_list_top = sort_and_count_key_skill(skills_txt)

    print(f'Вот ТОП 10 самых часто встречающихся навыков:')
    for skill, count in skills_list_top[:10]:
        print(f"{skill} - {count}")

    draw_pie_scatter(text_search, skills_list_top)


main()
