Пакет для простой работы с следующими API:
- GlobalProjectControl
- ProjectsApi
- AddSites

Создание объекта:
api_key(str, Ключ авторизациив api) - Получить можно на http://blacksmith.jooble.com/account/edit/
is_beta(bool, default=True) - Указатель на то, куда выполнять запросы

Пример:
from api import GlobalProjectControl
g = GlobalProjectControl(api_key="XXXX-XXXX-XXXX-XXXX", is_beta=False)

Добавление запросов .add_request():
- параметры для GlobalProjectControl:
    id_projects(list/str/int)   - id проектов к которым необходимо применить данное действие
    action(str)                 - Название действия которое необходимо выполнить
    value                       - Значение которое следует установить. Тип данных зависимости от исполняемого действия.
    Не обязательные параметры:
    looseMode(bool)             - Разрешает выполнять действия к валидным проектам. По умолчанию False
- параметры для ProjectsApi:
    id_projects(list/str/int)   - id проектов к которым необходимо применить данное действие
    action(str)                 - Название действия которое необходимо выполнить
    value                       - Значение которое следует установить. Тип данных зависимости от исполняемого действия
- параметры для AddSites:
    sites(list/str)             - Сайты для добавления в Crawler
    source(str)                 - Источник с которым мы будем добавлять сайты
    Не обязательные параметры:
    comment(str)                - Комментарий к транзакции, по умолчанию "Auto Add From Api"
    user_url_is_start_url(bool) - Установить добавляемый url как стартовую ссылку к проекту, по умолчанию False
    project_type_id             - Тип добавляемого проекта. По умолчанию 1 (обычный проект)
    is_ats                      - Указатель что данные сайты - АТС. По умолчанию False
    use_job_beagle              - Натравить на проекты программу JobBeagle - По умолчанию True

Выполнение запросов .exec():
- параметры:
    waiting(bool)             - Ожидать завершения запросов. Если запросов несколько - новый не начнётся
                                пока не завершится текущий. По умолчанию True
    notification(bool)        - Выводить уведомления при выполнении запросов. По умолчанию True
    thread_count(int)         - Количество потоков. Целесообразно использовать только для ProjectsApi. Не устанавливать
                                значение больше 20. Это может привести к лагам на blacksmith


Пример:
from api import ProjectsApi, AddSites

# Создаём объекты API
p = ProjectsApi(api_key="XXXX-XXXX-XXXX-XXXX", is_beta=False)
a = AddSites(api_key="XXXX-XXXX-XXXX-XXXX", is_beta=False)

# Добавляем запросы для выполнения
a.add_request(source="de_details_nr", sites=["http://test.com/test", "http://test1.com"], comment="Its a test",
              useJobBeagle=False, userUrlIsStartUrl=True)
p.add_request(id_projects=154613, action="Source", value="MyTestSource")

# Выполняем запросы
a.exec()
p.exec(notification=False, thread_count=20)


