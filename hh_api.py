import requests
import json
import database
import time

conn = database.create_connection('skillnestbot.db')


def get_list_id_vacancies(text):
    url_list = 'https://api.hh.ru/vacancies'
    list_id = []
    params = {'text': text}
    r = requests.get(url_list, params=params)
    found = json.loads(r.text)['found']

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

        print(f'iteration: {count}')
        print(f'vacancy_id: {vacancy_id}')
        print(f'vacancy_name: {vacancy_name}')

        count += 1
        if count % 29 == 0:
            time.sleep(5)


def get_and_store_key_skills(list_id):
    all_skills = ''
    for vac_id in list_id:
        data = get_data_vacancy(vac_id)
        vacancy_id = data.get('id')
        vacancy_name = data.get('name')
        key_skills = [skill['name'] for skill in data.get('key_skills', [])]
        skills = (', '.join((map(str, key_skills))))
        if key_skills:
            all_skills += skills
            # database.add_keys_kills_data(conn, vacancy_id, vacancy_name, skills)
        else:
            continue
    print(all_skills)


def main():
    # database.drop_table(conn, 'vacancy_data')
    # database.create_vacancy_data_table(conn)

    database.drop_table(conn, 'key_skills_data')
    database.create_keys_kills_data_table(conn)

    text_search = 'junior data science'
    list_id = get_list_id_vacancies(text_search)

    # get_and_store_vacancy(list_id)

    get_and_store_key_skills(list_id)


main()
