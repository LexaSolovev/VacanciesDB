import json

import requests


def get_employer_data(emp_hh_id: int) -> dict:
    """Функция получает данные по employer_id c сайта hh.ru"""
    response = requests.get(
        f"https://api.hh.ru/employers/{emp_hh_id}",
        headers={'User-Agent': 'HH-User-Agent'}
    )
    if response.status_code == 200:
        content = json.loads(response.content)
        return {
            "employer_id": emp_hh_id,
            "name": content["name"],
            "url": content["alternate_url"],
            "area_id": content["area"]["id"]
        }
    else:
        requests.RequestException(f"Неверный ответ! Статус-код = {response.status_code}")


def get_vacancies_by_employer(emp_hh_id: int) -> list[dict]:
    """Функция получает список вакансий по id работодателя с сайта hh.ru"""
    page = 0
    vacancies_list = []
    while page<3: # Забираем не более чем по 300 вакансий
        response = requests.get(
            "https://api.hh.ru/vacancies",
            params={'employer_id': emp_hh_id, 'page': page, 'per_page': 100},
            headers={'User-Agent': 'HH-User-Agent'}
        )
        page += 1
        if response.status_code == 200:
            content = json.loads(response.content)
            vacancies_list.extend(content['items'])
        else:
            requests.RequestException(f"Неверный ответ! Статус-код = {response.status_code}")
    return vacancies_list

if __name__ == "__main__":
    pass
    # with open(PATH_EMPLOYERS) as f:
    #     emp_list = json.load(f)["emp_hh_id"]
    # for emp_id in emp_list:
    #     print(get_employer_data(emp_id))
