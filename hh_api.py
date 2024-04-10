import requests
import json
import database

conn = database.create_connection('skillnestbot.db')


def get_list_id_vacancies(text):
    url_list = 'https://api.hh.ru/vacancies'
    list_id = []
    params = {'text': text, 'per_page': 100}
    r = requests.get(url_list, params=params)
    data = json.loads(r.text)
    found = data.get('found', 0)
    print(f'found: {found}')

    if found <= 1000:
        pages = (found + 99) // 100
    else:
        found = 1000
        pages = 10
        print("Количество найденных вакансий больше 1000. Ограничено до 1000.")

    for page in range(pages):
        params['page'] = page
        r = requests.get(url_list, params=params)
        data = json.loads(r.text)
        items = data.get('items', [])
        for vac in items:
            list_id.append(vac['id'])

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


def get_and_store_data(list_id):
    for vac_id in range(200):
        data = get_data_vacancy(list_id[vac_id])
        vacancy_id = data.get('id')
        vacancy_name = data.get('name')
        area = data.get('area', {}).get('name')
        salary_data = get_salary(data)
        salary_from = salary_data.get('from')
        salary_to = salary_data.get('to')
        currency = salary_data.get('currency')
        description = data.get('description')
        database.add_vacancy_data(conn, vacancy_id, vacancy_name, area, salary_from, salary_to, currency, description)


def main():
    database.drop_table(conn, 'vacancy_data')
    database.create_vacancy_data_table(conn)
    text_search = 'Junior Data Scientist'
    list_id = get_list_id_vacancies(text_search)
    # for key, value in enumerate(list_id):
    #     print(f"index: {key+1}, id: {value}")
    # print(list_id[120])
    # id = 96278252
    # null_count = list_id.count(None)
    # print("Количество значений None в массиве:", null_count)
    get_and_store_data(list_id)


main()
