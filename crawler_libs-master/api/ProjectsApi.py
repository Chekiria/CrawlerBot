from api.common.common import Api


class ProjectsApiError(Exception):
    pass


class ProjectsApi(Api):
    def __init__(self, api_key: str, is_beta: bool=True):
        super(ProjectsApi, self).__init__(api_key, is_beta)
        # Объявляем название вызваного класса в базовом классе
        self.api_name = __class__.__name__

        # Формируем урл к которому будем выполнять запросы
        base_url = "http://blacksmith.jooble.com_%BETTA%_/api/project/{0}/save"
        self.api_url_template = base_url.replace("_%BETTA%_", "") if is_beta is False else base_url.replace(
            "_%BETTA%_", ":4080")

    def add_request(self, **kwargs):
        """ Добавляем запросы к ProjectsApi

        :id_projects - Айди кравлерского проекта к оторому следует выполнить действие. Может быть int, str, list
        :action      - Название выполняемого действия - str
        :value       - Значение которое будет задано. Тип данных зависит от action
        """

        # Извлекаем папараметры
        id_projects = kwargs["id_projects"]
        action = kwargs["action"]
        value = kwargs["value"]

        # Делаем чтоб Api не крашилась если пользователь забыл обернуть id_projects в список
        if not isinstance(id_projects, list):
            id_projects = [id_projects]

        # Если нет проектов кторым нужно выполнять действие - не добавляем запрос
        if not id_projects:
            return

        # Накидываем елементы в список запросов
        for item in list(set(id_projects)):
            api_url = self.api_url_template.format(str(item).strip())
            self.api_requests.append({"api_url": api_url, action: value})

    def get_grouped_requests(self):
        """ Группирует запросы к Projects Api. Результат: 1 api_url = 1 запрос """
        grouped_request = []
        items_index = {}

        for request in self.api_requests:
            if request["api_url"] in items_index:
                index = items_index[request["api_url"]]
                exist_request = grouped_request[index].copy()

                for key, value in request.items():
                    if key == "api_url":
                        continue
                    elif key not in grouped_request[index]:
                        exist_request[key] = value
                        grouped_request[index] = exist_request
                    elif key in grouped_request[index] and grouped_request[index][key] != value:
                        raise ProjectsApiError("Duplicate Action {} in {}".format(key, request["api_url"]))
                    elif key in grouped_request[index] and grouped_request[index][key] == value:
                        pass
                    else:
                        raise ProjectsApiError("Queue generate. Impossible case")
            else:
                grouped_request.append(request)
                items_index[request["api_url"]] = len(grouped_request) - 1
        return grouped_request
