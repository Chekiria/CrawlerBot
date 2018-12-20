from api.GlobalProjectControl import GlobalProjectControlError
import logging
import json


class GlobalProjectControlParse:
    MAX_WAITING_TIME_SEC = 60 * 60
    WAITING_TIME = 5

    def __init__(self, api_key: str, is_beta: bool, user_request: dict, lock):
        self.api_key = api_key.strip()
        self.user_request = json.loads(user_request['body'])
        self.lock = lock

        base_url = "http://blacksmith.jooble.com{0}/GlobalControl/GetActionProgress"
        self.api_url = base_url.format("") if is_beta is False else base_url.format(":4080")

    def check_success_started(self, api_response):
        """ Разбираем ответ от API.
        Если API Успешно стартовало - Возвращаем сообщение об удачном старте
        Если API не стартовала - Кидаем исключение
        """
        if api_response.status_code == 200:
            if self.lock:
                with self.lock:
                    logging.debug("Action {0} started to run".format(self.user_request['action']))
        elif api_response.status_code == 400:
            raise GlobalProjectControlError("Input data is Invalid. Check your request: {0}".
                                            format(self.user_request))
        elif api_response.status_code == 403:
            raise GlobalProjectControlError("This action is not available for your account. {0}".
                                            format(self.user_request['action']))
        elif api_response.status_code == 500:
            raise GlobalProjectControlError("Something went wrong. Contact the developers for help")
        else:
            raise GlobalProjectControlError("Unknown response")

    def wait(self, api_response):
        """ Ожидание пока запрос к API не отработает полностью
        Если превышено время ожидания 1 час - кижаем исключение
        Если задание успешно завершилось возвращаем текстовое уведомление """
        from .GPC_Progress import get_global_project_api_action_status
        import datetime as dt
        import time

        # Фиксируем дату начала
        start_dt = dt.datetime.now()

        # Получаем id_transaction с ответа API
        api_response = api_response.json()
        transaction_id = api_response['id']

        # Выполняем запросы к global project api progress максимум 1 час, далее кидаем исключение
        response = None
        while (dt.datetime.now() - start_dt).seconds < GlobalProjectControlParse.MAX_WAITING_TIME_SEC:
            try:
                response, result = get_global_project_api_action_status(transaction_id=transaction_id,
                                                                        api_key=self.api_key, url=self.api_url)
            except Exception as e:
                raise GlobalProjectControlError("GlobalProjectControlProgress. {0}".format(e))

            if response:
                break
            else:
                time.sleep(GlobalProjectControlParse.WAITING_TIME)

        if not response:
            raise GlobalProjectControlError("Query running more then 1 hour. Check transaction yourself")

