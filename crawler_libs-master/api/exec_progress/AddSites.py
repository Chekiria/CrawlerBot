from exec_sql import Exec
from api.AddSites import AddSitesError

import logging
import json


class AddSitesParse:
    MAX_WAITING_TIME_SEC = 60 * 60
    WAITING_TIME = 30

    def __init__(self, is_beta: bool, user_request: dict, lock):
        self.user_request = json.loads(user_request['body'])
        self.db_name = 'Crawler' if is_beta is False else 'CrawlerTest'
        self.lock = lock

    def check_success_started(self, api_response):
        """ Разбираем ответ от API.
        Если API Успешно стартовало - Возвращаем сообщение об удачном старте
        Если API не стартовала - Кидаем исключение
        """
        # debug_message, info_message, warning_message
        if 200 >= api_response.status_code < 300:
            if self.lock:
                with self.lock:
                    logging.debug("{0} sites started to add".format(len(self.user_request['sites'])))
        else:
            raise AddSitesError("Unknown response")

    def wait(self, api_response=None):
        """ Ожидание пока запрос к API не отработает полностью
        Если превышено время ожидания 1 час - кижаем исключение
        Если задание успешно завершилось возвращаем текстовое уведомление """
        import datetime as dt
        import time

        # Получаем дату/время старта
        start_dt = dt.datetime.now()

        # Получаем параметры запроса пользователя, с помощью которых сможем идентифицировать id_transaction
        source = self.user_request['source']
        count_sites = len(self.user_request['sites'])

        # Задержка, т.к. транзакция могла не успеть создастся )
        time.sleep(AddSitesParse.WAITING_TIME)

        # Выполняем запрос к Базе и получаем id_transaction
        sql = "select top 1 id_insert from c_log_addsite with(nolock) where [source] = '{0}' and [count] = {1} " \
              "and [date] > cast(getdate() as date) order by [date] desc".format(source, count_sites)
        try:
            id_transaction = Exec().get_column(sql=sql, db_name=self.db_name)[0]
        except Exception:
            raise AddSitesError("Can`t get id_transaction")

        # Выполняем проверку максимум 1 час. Потом кидаем исключение
        response = False
        while (dt.datetime.now() - start_dt).seconds < AddSitesParse.MAX_WAITING_TIME_SEC:
            response = self.__check_transaction_finishing(id_transaction, count_sites)
            if response:
                break

            time.sleep(AddSitesParse.WAITING_TIME)

        if not response:
            raise AddSitesError("Query execute more then 1 hour. Check transaction yourself")

    def __check_transaction_finishing(self, id_transaction: str, count_sites: int) -> bool:
        """ Определяем завершилась ли транзакция.
        Выполняем запрос к DB. Узнаём сколько сайтов мы получили и сравниваем с кол-вом сайтов которое передавали """
        sql = "select count(*) from c_log_addsite_details with(nolock) where id_insert = {0}".format(id_transaction)
        try:
            count_added_sites = int(Exec().get_column(sql=sql, db_name=self.db_name)[0])
        except Exception:
            raise AddSitesError("Can`t get count added project. Id insert = {0}".format(id_transaction))
        return True if count_added_sites == count_sites else False

