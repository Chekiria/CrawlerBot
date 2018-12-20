import threading
import logging
import queue

API_KEY = ''
API_NAME = ''
IS_BETA = True
NOTIFICATION = True
WAITING = True
TASK = queue.Queue()
PRINT_LOCK = threading.Lock()


class ApiError(Exception):
    pass


class ExecApi(threading.Thread):
    """ Клас для выполнения запросов в потоках """
    def __init__(self):
        super(ExecApi, self).__init__()
        self.user_request = {}

    def run(self):
        import requests

        while not TASK.empty():
            try:
                self.user_request = TASK.get_nowait()
            except:
                break
            api_response = requests.post(url=self.user_request['api_url'], data=self.user_request['body'],
                                         headers=self.user_request['headers'])
            self.__parse_exec_result(api_response)

    def __parse_exec_result(self, api_response):
        # Создаём объект парсера результатов
        results_parser = self.__detect_parser()

        # Получаем уведомление о успешном старте. Если нужно - выводим его

        results_parser.check_success_started(api_response)

        # Ждём пока транзакция завершится
        if WAITING:
            results_parser.wait(api_response)

    def __detect_parser(self):
        if API_NAME == "AddSites":
            from api.exec_progress.AddSites import AddSitesParse
            return AddSitesParse(IS_BETA, self.user_request, lock=PRINT_LOCK if NOTIFICATION else None)

        elif API_NAME == 'GlobalProjectControl':
            from api.exec_progress.GlobalProjectControl import GlobalProjectControlParse
            return GlobalProjectControlParse(API_KEY, IS_BETA, self.user_request, lock=PRINT_LOCK if NOTIFICATION else None)

        elif API_NAME == "ProjectsApi":
            from api.exec_progress.ProjectsApi import ProjectsApiParse
            return ProjectsApiParse(API_KEY, IS_BETA, self.user_request, lock=PRINT_LOCK if NOTIFICATION else None)

        elif API_NAME == "AddSuggests":
            pass
        else:
            raise ApiError("Unknown api")


class Api:
    HEADERS = {'Content-Type': 'application/json; charset=utf-8'}

    def __init__(self, api_key: str, is_beta: bool=True):
        self.api_name = ''
        self.is_beta = is_beta
        self.api_key = api_key.strip()
        self.api_requests = []

    def __repr__(self):
        return str(len(self.get_grouped_requests())) if self.api_requests else "0"

    def add_request(self, **kwargs):
        pass

    def get_grouped_requests(self):
        pass

    def exec(self, waiting=True, notification=True, thread_count: int=1):
        logging.debug('----------[{0}]----------'.format(self.api_name))
        if notification and not self.api_requests:
            logging.warning("[{0}] Список запросов для API пуст. Завершаем работу API".format(self.api_name))
            logging.debug('----------[{0}]----------'.format(self.api_name))
            return None

        # Создаём очередь запросов к API, чистим предыдущие добавленные запросы
        my_queue = self.__generate_queue()
        self.api_requests = {}

        # Задаём настройки для выполнения запросов в потоках
        global API_KEY, API_NAME, IS_BETA, NOTIFICATION, WAITING, TASK
        API_KEY, API_NAME, IS_BETA = self.api_key, self.api_name, self.is_beta
        NOTIFICATION, WAITING, TASK = notification, waiting, my_queue

        # Создаём потоки
        threads = [ExecApi() for i in range(thread_count)]

        # Выполняем
        for item in threads:
            item.start()

        # Заканчиваем потоки
        for item in threads:
            item.join()
        logging.debug('----------[{0}]----------'.format(self.api_name))

    def __generate_queue(self):
        """ Превращаем наши запросы в очередь """
        import json

        my_queue = queue.Queue()
        request_groups = self.get_grouped_requests()
        for request in request_groups:
            # Извлекаем api_url, дописываем api_key
            api_url = request.pop("api_url")
            request["key"] = self.api_key

            # Помещаем запрос в очередь в валидном формате
            my_queue.put({"api_url": api_url, "body": json.dumps(request).encode('utf-8'), "headers": Api.HEADERS})
        return my_queue


def check_duplicates(list1: list, list2: list) -> list:
    return list(filter(lambda x: x in list2, list1))
