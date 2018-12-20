from api.common.common import Api, check_duplicates


class GlobalProjectControlError(Exception):
    pass


class GlobalProjectControl(Api):
    def __init__(self, api_key: str, is_beta: bool=True):
        super(GlobalProjectControl, self).__init__(api_key, is_beta)
        # Объявляем название вызваного класса в базовом классе
        self.api_name = __class__.__name__

        # Формируем урл к которому будем выполнять запросы
        base_url = "http://blacksmith.jooble.com{0}/GlobalControl"
        self.api_url = base_url.format("") if is_beta is False else base_url.format(":4080")

    def add_request(self, **kwargs):
        """ Добавляем запросы к Global Project Control Api

        :id_projects    - Айди кравлерского проекта к оторому следует выполнить действие. Может быть int, str, list
        :action         - Название выполняемого действия - str
        :value          - Значение которое будет задано. Тип данных зависит от action
        :apply_to_valid - Применять ли запросы к валидным проектам. Включает флаг looseMode в GPC. По умолчанию - выкл.
        """

        # Извлекаем папараметры
        apply_to_valid = kwargs.get("apply_to_valid", False)
        id_projects = kwargs["id_projects"]
        action = kwargs["action"]
        value = kwargs["value"]

        # Делаем чтоб Api не крашилась если пользователь забыл обернуть id_projects в список, переводим всё в str
        id_projects = [str(id_projects).strip()] if not isinstance(id_projects, list) else \
            list(map(lambda x: str(x).strip(), id_projects))

        # Если нет проектов кторым нужно выполнять действие - не добавляем запрос
        if not id_projects:
            return

        # Накидываем елементы в список запросов
        self.api_requests.append({"api_url": self.api_url, "looseMode": apply_to_valid,
                                  "projectIds": list(set(id_projects)), "action": action, "value": value})

    def get_grouped_requests(self):
        """  Группирует запросы к GlobalProjectControl. 1 - (action, value, apply_to_valid) = 1 запрос """
        grouped_request = []
        items_index = {}
        actions_index = {}

        # Группируем данные
        for request in self.api_requests:
            key = (request["action"], request["value"], request["looseMode"])
            if key in items_index:
                index = items_index[key]
                exist_query = grouped_request[index].copy()
                exist_query["projectIds"] = list(set(exist_query["projectIds"] + request["projectIds"]))
                grouped_request[index] = exist_query
            else:
                grouped_request.append(request)
                items_index[key] = len(grouped_request) - 1
                if request["action"] not in actions_index:
                    actions_index[request["action"]] = [len(grouped_request) - 1]
                else:
                    actions_index[request["action"]].append(len(grouped_request) - 1)

        # Проверка на наличие проекта в группах с одинаковым действием
        for action, indexes in actions_index.items():
            first_list = grouped_request[indexes[0]]["projectIds"]
            for index in indexes[1:]:
                second_list = grouped_request[index]["projectIds"]

                duplicate = check_duplicates(first_list, second_list)
                if duplicate:
                    raise GlobalProjectControlError("Duplicate projects {}".format(','.join(duplicate)))

                first_list = grouped_request[index]["projectIds"]

        # Переводим id_project в формат, понятный для GPC
        for i, item in enumerate(grouped_request):
            new_item = item.copy()
            new_item["projectIds"] = ",".join(item["projectIds"])
            grouped_request[i] = new_item

        return grouped_request
