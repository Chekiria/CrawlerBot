from common import get_system_info, write_tsv, write_json, drop_duplicates
import configparser
import logging
import pyodbc
import json
import os


DEFAULT_CONFIG_FILE = __file__.replace(".py", ".ini")


class Exec:
    def __init__(self, config_file: str=DEFAULT_CONFIG_FILE, db_name: str=None):
        self.__credentials = {}
        self.__connection = None
        self.db_name = db_name

        self.__get_credentials(config_file)
        if db_name:
            self.__connect_to_db(db_name)

    def __repr__(self):
        return str(list(self.__credentials.keys()))

    def __del__(self):
        if self.__connection:
            logging.debug("Соеденение прервано")
            self.__connection.close()
            self.__connection = None

    def __get_credentials(self, config_file):
        """ Загружаем credentials с файла config """
        logging.debug("Генерируем credentials для соеденения с БД")
        config = configparser.ConfigParser()
        config.read(config_file)

        keys = config.sections()

        j_sections, j_dict = ("Job", "SRVDATA"), {}
        for s in j_sections:
            j_dict[s] = None
            if s in keys:
                j_dict[s] = dict(config[s])
                config.remove_section(s)

        if j_dict["Job"]:
            srv = j_dict["SRVDATA"]["srv_data_path"] if j_dict["SRVDATA"] else "C:/JoobleListPath/srvdata.json"
            auth = j_dict["Job"]
            self.__generate_job_credentials(srv, auth)

        for db_name in config:
            items_dict = {k: v for k, v in config[db_name].items()}
            self.__credentials[db_name] = items_dict

    def __generate_job_credentials(self, srv_data_path: str, auth_data: dict):
        """ Формируем credentials для прод серверов """
        server_data_dict = json.load(open(srv_data_path, 'rt', encoding='utf-8'))

        for instance in server_data_dict["SqlInstanceList"]:
            for country in instance["CountryList"]:
                # К логину и паролю дописываем имя сервера и добавляем результат в credentials
                credentials = auth_data.copy()
                credentials["server"] = instance["Name"]
                self.__credentials["Job_{}".format(country.upper().strip())] = credentials

    def __connect_to_db(self, db_name: str):
        self.__del__()

        if db_name not in self.__credentials:
            db_name = "Job_{}".format(db_name.upper().strip())

        database = "{" + db_name + "}"
        server = "{" + self.__credentials[db_name]['server'] + "}"
        username = '{' + self.__credentials[db_name]['login'] + '}'
        password = '{' + self.__credentials[db_name]['pass'] + '}'
        self.__connection = pyodbc.connect('DRIVER=' + self.__get_driver() + ';SERVER=' + server + ';DATABASE=' +
                                           database + ';UID=' + username + ';PWD=' + password, timeout=0)
        logging.debug("Установлено соеденение с {0}".format(db_name))

    def __exec(self, sql: str, return_result=False):
        """ Выполняем запрос к БД. Если задано - возвращаем результат """
        cur, values, column_names = None, None, None
        try:
            if not sql:
                logging.warning("Запрос SQL пуст. Выполнение прекращено")
                return

            cur = self.__connection.cursor()
            cur.execute(sql)
            if return_result:
                values = cur.fetchall()
                column_names = [column[0] for column in cur.description]
            cur.commit()
        except Exception:
            if cur:
                cur.rollback()
            raise

        return (values, column_names) if return_result else None

    def get_rows(self, sql, db_name=None, **kwargs):
        """ По-умолчанию возвращает результат в виде: [ (val1, val2), (val3, val4) ]
        :sql            - запрос или файл с запросом, который будет выполнятся
        :db_name        - если задано подключаемся к указаной БД при условии, что мы уже к ней уже не подключены. После
                        выполнения запроса возвращается предыдущие соеденение (если такое было установлено при создании
                        объекта класа, иначе - просто отключаемся)
        :as_dict        - вернуть результат в виде:
                        [ {col_name1: value, col_name2: value2}, {col_name1: value3, col_name2: value4} ]
        :func_cleaner   - если задано - функция применяется ко всем елементам, котороые были выбоаны запросом.
        :fp             - если задано - записываем результат в файл
        :encoding       - кодировка, в которой необходимо записывать данные в файл
        """
        # Получаем значения
        as_dict = kwargs.get("as_dict", False)
        func = kwargs.get("func_cleaner", lambda x: x)
        fp = kwargs.get("fp", None)
        encoding = kwargs.get("encoding", "utf-8")

        # Если нужно выполнить запрос к БД, не заданной при создании объекта класса
        if db_name and self.db_name != db_name:
            self.__connect_to_db(db_name)

        # Выполняем sql
        sql = self.__get_working_sql(sql)
        data = self.__exec(sql=sql, return_result=True)

        # Если подключались к другой БД - возвращаем первоначальное соеденение
        if not self.db_name:
            self.__del__()
        elif db_name and self.db_name != db_name:
            self.__connect_to_db(self.db_name)

        # Обрабатываем кейсы когда sql запрос не вернул данных
        if not data or not data[0]:
            result = []
        else:
            values, column_names = data[0], data[1]
            # Обрабатываем кейс, когда нужно возвращать list of tuples
            if not as_dict:
                result = [tuple(map(lambda x: func(str(x)), item)) for item in values]
                if fp:
                    write_tsv(data=result, fp=fp, encoding=encoding)

            # Обрабатываем кейс, когда нужно возвращать list of dicts
            else:
                result = [dict(zip(column_names, tuple(map(lambda x: func(str(x)), row)))) for row in values]
                if fp:
                    write_json(data=result, fp=fp, encoding=encoding)

        return result

    def get_column(self, sql, db_name=None, **kwargs):
        """ По-умолчанию возвращает результат в виде: [ val1, val2, val3, val4 ]
        :sql            - запрос или файл с запросом, который будет выполнятся
        :db_name        - если задано подключаемся к указаной БД при условии, что мы уже к ней уже не подключены. После
                        выполнения запроса возвращается предыдущие соеденение (если такое было установлено при создании
                        объекта класа, иначе - просто отключаемся)
        :func_cleaner   - если задано - функция применяется ко всем елементам, котороые были выбоаны запросом.
        :fp             - если задано - записываем результат в файл
        :encoding       - кодировка, в которой необходимо записывать данные в файл
        :duplicates     - допускать дубликаты в записях. По умолчанию True
        """
        # Получаем значения
        func = kwargs.get("func_cleaner", lambda x: x)
        fp = kwargs.get("fp", None)
        encoding = kwargs.get("encoding", "utf-8")
        duplicates = kwargs.get("duplicates", True)

        # Если нужно выполнить запрос к БД, не заданной при создании объекта класса
        if db_name and self.db_name != db_name:
            self.__connect_to_db(db_name)

        # Выполняем sql
        sql = self.__get_working_sql(sql)
        data = self.__exec(sql=sql, return_result=True)

        # Если подключались к другой БД - возвращаем первоначальное соеденение
        if not self.db_name:
            self.__del__()
        elif db_name and self.db_name != db_name:
            self.__connect_to_db(self.db_name)

        # Обрабатываем кейсы когда sql запрос не вернул данных
        if not data or not data[0]:
            result = []
        else:
            values, column_names = data[0], data[1]
            result = list(map(lambda x: func(str(x[0])), values))

        # Если нужно - удаляем дубликаты
        if not duplicates:
            result = drop_duplicates(result)

        # Если нужно - записываем результат в файл
        if fp:
            write_tsv(data=result, fp=fp, encoding=encoding)

        return result

    def exec(self, sql, db_name=None, **kwargs):
        """ Этот метод ничего не возвращает
        :sql            - запрос или файл с запросом, который будет выполнятся
        :db_name        - если задано подключаемся к указаной БД при условии, что мы уже к ней уже не подключены. После
                        выполнения запроса возвращается предыдущие соеденение (если такое было установлено при создании
                        объекта класа, иначе - просто отключаемся)
        :exec_size      - кол-во запросов исполняемых за 1 раз. Применяется в случае если в параметр sql был передан
                        список запросов (к примеру 100500 inset into). По умолчанию - 100
        """
        # Получаем параметры
        exec_size = kwargs.get("exec_size", 100)

        # Если нужно выполнить запрос к БД, не заданной при создании объекта класса
        if db_name and self.db_name != db_name:
            self.__connect_to_db(db_name)

        # Обрабатываем кейс когда нужно выполнять запросы частями
        if isinstance(sql, list) and len(sql) > exec_size:
            for i in range(0, len(sql), exec_size):
                logging.debug("Выполняем запросы [{0} - {1}]".format(i, i + exec_size))
                exec_part = '\n'.join(sql[i: i + exec_size])
                self.__exec(sql=exec_part, return_result=False)

        # Обрабатываем все остальные кейсы
        else:
            if isinstance(sql, list):
                sql_to_exec = '\n'.join(sql)
            elif isinstance(sql, str):
                sql_to_exec = self.__get_working_sql(sql)
            else:
                raise Exception("Exec. Unknown sql format. Must be list/str or file_path")

            self.__exec(sql=sql_to_exec, return_result=False)

        # Если подключались к другой БД - возвращаем первоначальное соеденение
        if not self.db_name:
            self.__del__()
        elif db_name and self.db_name != db_name:
            self.__connect_to_db(self.db_name)

    @staticmethod
    def __get_working_sql(sql):
        if len(sql) < 200 and os.path.isfile(sql):
            sql = open(sql, "rt", encoding="utf-8").read()
        return sql

    @staticmethod
    def __get_driver():
        cur_os = get_system_info()['os']
        if cur_os == 'nt':
            return '{SQL Server}'
        elif cur_os == 'posix':
            return '{ODBC Driver 13 for SQL Server}'
        else:
            raise Exception("Unknown OS. Can`t use exec_sql on this platform")