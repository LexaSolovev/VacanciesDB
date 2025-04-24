import json

import requests

from config import PATH_EMPLOYERS


def get_employer_data(emp_hh_id: int) -> dict:
    """Функция получает данные по employer_id c сайта hh.ru"""
    response = requests.get(
        f"https://api.hh.ru/employers/{emp_hh_id}",
        headers={'User-Agent': 'HH-User-Agent'}
    )
    if response.status_code == 200:
        content = json.loads(response.content)
        return {
            "name": content["name"],
            "url": content["alternate_url"],
            "hh_id": emp_hh_id,
            "area_id": content["area"]["id"]
        }
    else:
        requests.RequestException("Неверный ответ!")


def get_vacancies_by_employer(emp_hh_id: int) -> list[dict]:
    pass

if __name__ == "__main__":
    with open(PATH_EMPLOYERS) as f:
        emp_list = json.load(f)["emp_hh_id"]
    for emp_id in emp_list:
        print(get_employer_data(emp_id))