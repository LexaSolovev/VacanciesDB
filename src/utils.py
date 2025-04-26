import json
import os

import psycopg2
from dotenv import load_dotenv

from config import PATH_AREAS, PATH_EMPLOYERS
from src.api import get_employer_data, get_vacancies_by_employer

#Загрузка переменных из .env файла
load_dotenv()


def get_params_for_connect_db() -> dict:
    """
    Функция для получения параметров для подключения к базе данных из .env файла
    :return: возвращает словарь с параметрами для подключения к БД: 'db_name', 'user', 'password', 'host', 'port'
    """
    return {
        'dbname': os.getenv("DB_NAME"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'host': os.getenv("DB_HOST"),
        'port': os.getenv("DB_PORT")
    }

def create_database() -> None:
    """
    Функция для создания новой базы данных PostgreSQL.

    Параметры берутся из .env файла:
    db_name (str): имя создаваемой базы данных.
    user (str): имя пользователя PostgreSQL.
    password (str): пароль пользователя PostgreSQL.
    host (str): хост PostgreSQL, по умолчанию 'localhost'.
    port (str): порт PostgreSQL, по умолчанию '5432'.
    """
    params = get_params_for_connect_db()
    dbname = params['dbname']
    user = params['user']
    password = params['password']
    host = params['host']
    port = params['port']
    try:
        # Подключение к серверу PostgreSQL
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port
        )
        connection.autocommit = True  # Автокоммит для команд управления базой данных

        # Создание новой базы данных
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT datname from pg_database WHERE datname = '{dbname}'")
            if not cursor.fetchall():
                cursor.execute(f"CREATE DATABASE {dbname}")
                print(f"База данных {dbname} успешно создана.")



    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к серверу PostgreSQL: {e}")
    except psycopg2.ProgrammingError as e:
        print(f"Ошибка при создании базы данных {dbname}: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    finally:
        try:
            connection.close()
        finally:
            pass


def create_all_tables():
    params = get_params_for_connect_db()
    try:
        connection = psycopg2.connect(**params)
        connection.autocommit = True
    except Exception as e:
        print(f"Ошибка при попытке подключения к серверу PostgreSQL: {e}")
        return
    with (connection.cursor() as cursor):
        try:
            #Создаем таблицу регионов
            query = ("CREATE TABLE IF NOT EXISTS areas("
                     "area_id INT PRIMARY KEY,"
                     "parent_id INT,"
                     "name VARCHAR(250) NOT NULL)")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)

        try:
            #Создаем таблицу работодателей
            query = ("CREATE TABLE IF NOT EXISTS employers("
                     "employer_id INT PRIMARY KEY,"
                     "name VARCHAR(250) NOT NULL,"
                     "url VARCHAR(500) NOT NULL,"
                     "area_id INT NOT NULL, "
                     "FOREIGN KEY (area_id) REFERENCES areas(area_id))")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)

        try:
            #Создаем таблицу вакансий
            query = ("CREATE TABLE IF NOT EXISTS vacancies("
                     "vacancy_id INT PRIMARY KEY,"
                     "name VARCHAR(500) NOT NULL,"
                     "url VARCHAR(500) NOT NULL,"
                     "employer_id INT,"
                     "salary_from INT NOT NULL DEFAULT 0," 
                     "salary_to INT NOT NULL DEFAULT 0,"
                     "currency VARCHAR(5) NOT NULL DEFAULT 'RUR',"
                     "description TEXT,"
                     "FOREIGN KEY (employer_id) REFERENCES employers(employer_id))")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)
        finally:
            connection.close()
            return


def load_areas_from_json():
    with open(PATH_AREAS) as f:
        areas_data = json.load(f)
    params = get_params_for_connect_db()
    connection = psycopg2.connect(**params)
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE areas CASCADE")
        def add_area_to_table(data: dict) -> None:
            """Вспомогательная рекурсивная функция для обработки и добавления записей из древовидной структуры"""
            area_id = data['id']
            parent_id = data['parent_id'] if data['parent_id'] else 'null'
            name = data['name']
            insert_data = (area_id, parent_id, name)
            query = ("INSERT INTO areas(area_id, parent_id, name) "
                      "VALUES (%s, %s, %s)")
            cursor.execute(query, insert_data)
            for area in data['areas']:
                add_area_to_table(area)

        for area in areas_data:
            add_area_to_table(area)
    connection.close()


def load_employers_to_db() -> None:
    """Записывает данные по списку работодателей в таблицу employers"""
    with open(PATH_EMPLOYERS) as f:
        emp_list = json.load(f)["emp_hh_id"]
    params = get_params_for_connect_db()
    connection = psycopg2.connect(**params)
    connection.autocommit = True
    with connection.cursor() as cursor:
        for emp_id in emp_list:
            emp_data = get_employer_data(emp_id)
            insert_data = (emp_data['employer_id'], emp_data['name'], emp_data['url'], emp_data['area_id'])
            query = "INSERT INTO employers(employer_id, name, url, area_id) VALUES(%s,%s,%s,%s)"
            cursor.execute(query, insert_data)


def load_vacancies_to_db() -> None:
    params = get_params_for_connect_db()
    connection = psycopg2.connect(**params)
    connection.autocommit = True
    with connection.cursor() as cursor:
        query = "SELECT employer_id FROM employers"
        cursor.execute(query)
        query_result = cursor.fetchall()
        emp_list = [row[0] for row in query_result] # Получаем список employers_id

        for emp_id in emp_list:
            vacancies_data = get_vacancies_by_employer(emp_id)

            for vacancy in vacancies_data:
                salary_from, salary_to, currency = validate_salary(vacancy['salary'])
                insert_data = (
                    vacancy['id'],
                    vacancy['name'],
                    vacancy['alternate_url'],
                    emp_id,
                    salary_from,
                    salary_to,
                    currency,
                    vacancy['snippet'].get('requirement', 'null')
                )
                query = ("INSERT INTO vacancies VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
                         "ON CONFLICT (vacancy_id) DO NOTHING")

                # При конфликте по vacancy_id новая запись не добавляется.

                cursor.execute(query, insert_data)

    connection.close()


def validate_salary(salary_info: dict | None) -> tuple:
    """ Метод для валидации информации о зарплате, возвращает картеж (salary_from, salary_to, currency) """
    salary_from = 0
    salary_to = 0
    currency = "RUR"
    if salary_info:
        salary_from = salary_info["from"] if salary_info["from"] else 0
        salary_to = salary_info["to"] if salary_info["to"] else 0
        currency = salary_info["currency"] if salary_info["currency"] else "RUR"
    return salary_from, salary_to, currency







def user_interaction() -> None:
    """
    Функция для взаимодействия с пользователем
    """
    # Создание БД и таблиц
    create_database()
    create_all_tables()

    # Загрузка данных о регионах, работодателях и вакансиях в БД
    load_areas_from_json()
    load_employers_to_db()
    load_vacancies_to_db()


