import psycopg2


class DBManager:

    def __init__(self, params: dict):
        self.__params = params
        self.__connection = psycopg2.connect(**self.__params)
        self.__cursor = self.__connection.cursor()

    def __del__(self):
        self.__cursor.close()
        self.__connection.close()

    def get_companies_and_vacancies_count(self):
        """ Функция для получения списка компаний с количеством вакансий
         Возвращает курсор
        """
        cursor = self.__cursor
        query = ("select e.name, count(v.vacancy_id) "
                 "from employers e "
                 "left join vacancies v "
                 "using(employer_id) "
                 "group by e.name")
        cursor.execute(query)
        return cursor

    def get_all_vacancies(self):
        cursor =  self.__cursor
        query = ("select e.name as Employer_Name, v.name as Vacancy, salary_from, salary_to, v.url "
                 "from employers e "
                 "join vacancies v "
                 "using(employer_id)"
                 "order by e.name, v.name")
        cursor.execute(query)
        return cursor

    def get_avg_salary(self):
        cursor = self.__cursor
        query = "select (avg(salary_to)+avg(salary_from))/2 as avg_salary from vacancies"
        cursor.execute(query)
        return cursor

    def get_vacancies_with_higher_salary(self):
        cursor = self.__cursor
        query = ("select v.vacancy_id, v.name, v.salary_from, v.salary_to, v.url from vacancies v "
                 "where salary_from > ("
                 "select (avg(salary_to)+avg(salary_from))/2"
                 " from vacancies)")
        cursor.execute(query)
        return cursor

    def get_vacancies_with_keyword(self, keyword: str):
        cursor = self.__cursor
        query = ("select v.vacancy_id, v.name, v.salary_from, v.salary_to, v.url from vacancies v "
                 "where "
                 "v.name "
                 "ilike "
                 f"'%{keyword}%' ")
        cursor.execute(query)
        return cursor

    def print_table(self, cursor):
        # Получаем имена столбцов
        column_names = [desc[0] for desc in cursor.description]

        # Определяем максимальную ширину столбцов
        column_widths = [max(len(str(value)) for value in row) for row in zip(*cursor.fetchall())]
        column_widths = [max(len(name), width) for name, width in zip(column_names, column_widths)]

        # Выводим заголовок таблицы
        print(' '.join(f'{name:{width}}' for name, width in zip(column_names, column_widths)))
        print('-' * (sum(column_widths) + len(column_widths)))

        # Возвращаемся к началу набора результатов
        cursor.scroll(0, mode='absolute')

        # Выводим результаты запроса
        for row in cursor.fetchall():
            print(' '.join(f'{value:{width}}' for value, width in zip(row, column_widths)))
        # Итоговый разделитель
        print('-' * (sum(column_widths) + len(column_widths)))


# if __name__ == "__main__":
#     params = get_params_for_connect_db()
#     db_manager = DBManager(params)
#     # result = db_manager.get_companies_and_vacancies_count()
#     # db_manager.print_table(result)
#     # result = db_manager.get_all_vacancies()
#     # db_manager.print_table(result)
#     # result = db_manager.get_avg_salary()
#     # db_manager.print_table(result)
#     # result = db_manager.get_vacancies_with_higher_salary()
#     # db_manager.print_table(result)
#     result = db_manager.get_vacancies_with_keyword("python")
#     db_manager.print_table(result)