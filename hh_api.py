import requests
import json

'''
TODO: 
- MAX NUMBER OF VACANCIES??? 500 maybe
- TABLE FOR VACANCIES DATA
and some other staff
'''
def get_list_id_vacancies(text):
    url_list = 'https://api.hh.ru/vacancies'
    list_id = []
    params = {'text': text, 'per_page': 100}  # Установка per_page не больше 100
    r = requests.get(url_list, params=params)
    data = json.loads(r.text)
    found = data.get('found', 0)  # Получение количества найденных вакансий
    print(f'found: {found}')

    if found <= 100:  # Проверка, если найдено не больше 100 вакансий
        items = data.get('items', [])
        for vac in items:
            list_id.append(vac['id'])
    else:
        pages = (found + 99) // 100  # Вычисление количества страниц
        for page in range(pages):  # Перебор всех страниц
            params['page'] = page
            r = requests.get(url_list, params=params)
            data = json.loads(r.text)
            items = data.get('items', [])
            print(items)
            for vac in items:
                list_id.append(vac['id'])

    return list_id


# def get_vacancy(id):
#     url_vac = 'https://api.hh.ru/vacancies/%s'
#     r = requests.get(url_vac % id)
#
#     return json.loads(r.text)


text = 'Data Scientist'
list_id = get_list_id_vacancies(text)
print(list_id)


