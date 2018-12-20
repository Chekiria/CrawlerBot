from api.ProjectsApi import ProjectsApiError
import logging


class ProjectsApiParse:
    MAX_WAITING_TIME_SEC = 60 * 60
    WAITING_TIME = 5

    def __init__(self, api_key: str, is_beta: bool, user_request: dict, lock):
        self.status_code = None
        self.lock = lock

        self.current_project = user_request["api_url"].split('/')[-2]
        self.api_key = api_key.strip()

        base_url = "http://blacksmith.jooble.com{0}/GlobalControl/GetActionProgress"
        self.api_url = base_url.format("") if is_beta is False else base_url.format(":4080")

    def check_success_started(self, api_response, lock=None):
        """ Разбираем ответ от API.
        Если API Успешно стартовало - Возвращаем сообщение об удачном старте
        Если API не стартовала - Кидаем исключение """
        self.status_code = api_response.status_code
        if api_response.status_code == 200:
            try:
                api_response = api_response.json()
            except Exception:
                raise Exception("Can`t connect to CrawlerWeb. Check your api_key")
            self.__parse_200_response(api_response, lock)
        elif api_response.status_code == 202:
            if self.lock:
                with self.lock:
                    logging.debug("Project {} wait GlobalProjectControl finishing".format(self.current_project))
        elif api_response.status_code == 404:
            if self.lock:
                with self.lock:
                    logging.warning("Project {} does not exist".format(self.current_project))
        elif api_response.status_code == 500:
            raise ProjectsApiError("Something went wrong. Contact the developers for help")
        else:
            raise ProjectsApiError("Unknown response status code")

    def wait(self, api_response, lock=None):
        """ Ожидание пока запрос к API не отработает полностью
        Если превышено время ожидания 1 час - кижаем исключение
        Если задание успешно завершилось возвращаем текстовое уведомление """
        if self.status_code and self.status_code == 202:
            from .GPC_Progress import get_global_project_api_action_status
            import datetime as dt
            import time

            # Фиксируем дату начала
            start_dt = dt.datetime.now()

            # Получаем id_transaction с ответа API
            try:
                api_response = api_response.json()
                transaction_id = api_response['id']
            except:
                raise Exception("Can`t connect to CrawlerWeb. Check your api_key")

            # Выполняем запросы к global project api progress максимум 1 час, далее кидаем исключение
            response = None
            while (dt.datetime.now() - start_dt).seconds < ProjectsApiParse.MAX_WAITING_TIME_SEC:
                try:
                    response, result = get_global_project_api_action_status(transaction_id=transaction_id,
                                                                            api_key=self.api_key, url=self.api_url)
                except Exception as e:
                    raise ProjectsApiError("GlobalProjectControlProgress. {0}".format(e))

                if response:
                    self.__parse_200_response(result, lock)

                else:
                    time.sleep(ProjectsApiParse.WAITING_TIME)

            if not response:
                raise ProjectsApiError("Query running more then 1 hour. Check transaction yourself")

    def __parse_200_response(self, api_response, lock):
        """ Разбирает 200 ответ api, возврашает сообщение """
        if api_response.get('mode') == 'blacklisted':
            if self.lock:
                with self.lock:
                    logging.warning("Project {0} send to blacklist after change".format(self.current_project))

        elif api_response.get('mode') == 'frozen':
            if self.lock:
                with self.lock:
                    logging.warning("Project {0} send to frozen after change".format(self.current_project))

        elif api_response.get('mode') == 'ok':
            if self.lock:
                with self.lock:
                    logging.debug("Project {0} was success changed".format(self.current_project))
        else:
            if self.lock:
                with self.lock:
                    logging.warning("Project {0} has errors: {1}".format(self.current_project, api_response.get('errors')))
