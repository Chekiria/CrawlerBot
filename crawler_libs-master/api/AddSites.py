from api.common.common import Api, check_duplicates


class AddSitesError(Exception):
    pass


class AddSites(Api):
    def __init__(self, api_key: str, is_beta: bool=True):
        super(AddSites, self).__init__(api_key, is_beta)
        # Объявляем название вызваного класса в базовом классе
        self.api_name = __class__.__name__

        # Формируем урл к которому будем выполнять запросы
        base_url = "http://blacksmith.jooble.com{0}/AddSites/UploadSitesNew/"
        self.api_url = base_url.format("") if is_beta is False else base_url.format(":4080")

    def add_request(self, **kwargs):
        """ Добавляем запросы к Add Sites Api

        :sites(str/list)                            - Список сайтов которые нужно добавить
        :source(str)                                - Источник (c_project.source_country) в который будут добавлятся
                                                      сайты
        :comment(str, default="Auto Add From Api")  - Комендарий к транзакции AddSite
        :user_url_is_start_url(bool, default=False) - Флаг указывающий что необходимо установить передаваемый урл старт
                                                      урлом проекта
        :project_type_id(int, default=1)            - тип добавляемых проектов. 1- обычный, 3-Single, 4-Partial
        :is_ats(bool, default=False)                - Флаг указывающий что добавляемые сайты - АТС. Отдельная логика
                                                      для добавления
        :use_job_beagle(bool, default=True)         - Переводить сайты в статус Virgin, где они будут обрабатыватся
                                                      программой JobBeagle.
        """

        # Извлекаем параметры
        sites = kwargs["sites"]
        source = kwargs["source"]

        # Если нет сайтов которые необходимо добавлять - не добавляем запрос
        if not sites:
            return

        comment = kwargs.get("comment", "Auto Add From Api")
        user_url_is_start_url = kwargs.get("user_url_is_start_url", False)
        project_type_id = kwargs.get("project_type_id", 1)
        is_ats = kwargs.get("is_ats", False)
        use_job_beagle = kwargs.get("use_job_beagle", True)

        # Делаем чтоб Api не крашилась если пользователь забыл обернуть sites в список, делаем всем елементам strip
        sites = [str(sites).strip()] if not isinstance(sites, list) else list(map(lambda x: x.strip(), sites))

        self.api_requests.append({"api_url": self.api_url, "source": source, "sites": list(set(sites)),
                                  "comment": comment, "userUrlIsStartUrl": user_url_is_start_url,
                                  "projectTypeId": project_type_id, "isAts": is_ats, "useJobBeagle": use_job_beagle})

    def get_grouped_requests(self):
        """  Группирует запросы к AddSites.
        1 - (source, comment, user_url_is_start_url, project_type_id, is_ats, use_job_beagle) = 1 запрос """
        grouped_request = []
        items_index = {}

        # Группируем данные
        for request in self.api_requests:
            key = (request["source"], request["comment"], request["userUrlIsStartUrl"], request["projectTypeId"],
                   request["isAts"], request["useJobBeagle"])

            if key in items_index:
                index = items_index[key]
                exist_query = grouped_request[index].copy()
                exist_query["sites"] = list(set(exist_query["sites"] + request["sites"]))
                grouped_request[index] = exist_query
            else:
                grouped_request.append(request)
                items_index[key] = len(grouped_request) - 1

        # Проверка не дублируются ли сайты для добавления
        first_list = grouped_request[0]["sites"]
        for item in grouped_request[1:]:
            second_list = item["sites"]

            duplicate = check_duplicates(first_list, second_list)
            if duplicate:
                raise AddSitesError("Duplicate sites {}".format(','.join(duplicate)))

            first_list = item["sites"]
        return self.partition_to_parts(grouped_request)

    @staticmethod
    def partition_to_parts(grouped_request_list: list, max_sites: int = 2000) -> list:
        """ Разбиваем слишком большие запросы к AddSites на несколько мелких """
        import math
        requests_to_exec = []
        for request in grouped_request_list:
            # Если количество сайтов - допустимого размера
            if len(request["sites"]) <= max_sites:
                requests_to_exec.append(request)
                continue

            # Если количество сайтов - слишком большое - считаем на сколько частей его нужно разбивать
            sites = request.pop("sites")
            count_parts = math.ceil(len(sites) / max_sites)

            # Разбиваем запрос на части
            for i in range(0, count_parts):
                new_request = request.copy()
                new_request["sites"] = sites[i * max_sites: (i + 1) * max_sites]
                requests_to_exec.append(new_request)

        return requests_to_exec
