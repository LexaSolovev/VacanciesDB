import os

import psycopg2
from dotenv import load_dotenv

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
            query = ("CREATE TABLE areas("
                     "area_id INT PRIMARY KEY,"
                     "parent_id INT NOT NULL,"
                     "name VARCHAR(250) NOT NULL)")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)

        try:
            #Добавляем внешний ключ для parent_id
            query = ("ALTER TABLE areas "
                     "ADD CONSTRAINT FK_ParentArea "
                     "FOREIGN KEY(parent_id) REFERENCES "
                     "areas(area_id)")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)

        try:
            #Создаем таблицу работодателей
            query = ("CREATE TABLE employers("
                     "employer_id SERIAL PRIMARY KEY,"
                     "name VARCHAR(250) NOT NULL,"
                     "url VARCHAR(500) NOT NULL,"
                     "hh_id INT NOT NULL,"
                     "area_id INT NOT NULL, "
                     "FOREIGN KEY (area_id) REFERENCES areas(area_id))")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)

        try:
            #Создаем таблицу вакансий
            query = ("CREATE TABLE vacancies("
                     "vacancy_id SERIAL PRIMARY KEY,"
                     "name VARCHAR(250) NOT NULL,"
                     "url VARCHAR(500) NOT NULL,"
                     "hh_id INT NOT NULL,"
                     "employer_id INT,"
                     "salary_from INT NOT NULL," 
                     "salary_to INT NOT NULL,"
                     "currency VARCHAR(5) NOT NULL,"
                     "description TEXT,"
                     "FOREIGN KEY (employer_id) REFERENCES employers(employer_id))")
            cursor.execute(query)

        except psycopg2.ProgrammingError as e:
            print(f"Ошибка при выполнении запроса: {query}")
            print(e)
        finally:
            connection.close()
            return



def user_interaction() -> None:
    """
    Функция для взаимодействия с пользователем
    """
    create_database()
    create_all_tables()