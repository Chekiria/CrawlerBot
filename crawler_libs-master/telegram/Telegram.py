import configparser
import json
import requests

DEFAULT_CONFIG_FILE = __file__.replace(".py", ".ini")


class Telegram:
    def __init__(self, config_file: str=DEFAULT_CONFIG_FILE):
        self._config_file = config_file
        self._token, self._known_chats = self._parse_config()

    def _parse_config(self):
        config = configparser.ConfigParser()
        config.read(self._config_file)
        known_chats = {k: int(v) for k, v in config.items('KnownChats')}
        return config['BotToken']['bot_token'], known_chats

    def get_known_chats(self):
        return self._known_chats

    def send(self, msg: str, to: str):
        reciever = to.lower()
        if reciever not in self._known_chats.keys():
            print("[Telegram] Warning UNKNOWN_RECEIVER [{0}]\n"
                  "\tThis user must write at least one message to @DDNotificationsBot.\n"
                  "\tthen call manually 'Telegram.update_chats()' and try again.".format(to))
            return

        chat_id = self._known_chats[reciever]
        url = "https://api.telegram.org/bot{0}/sendMessage".format(self._token)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "markdown"}).encode("utf-8")
        response = requests.post(url=url, data=data, headers=headers)

        if response.status_code != 200:
            print("[Telegram] Error BAD_STATUS_CODE [{0}] data [{1}]".format(response.status_code, response.content))
            return

        print("[Telegram] Message to [{0}] sent successfully".format(reciever))

    def update_chats(self):
        # Получаем список всех известных чатов
        updates = self.__get_updates()

        new_chats = dict()
        for update in updates:
            # Если текущий update НЕ сообщение: пропускаем
            if 'message' not in update.keys():
                continue

            chat = update['message']['chat']

            name, chat_id = None, None
            # Обрабатываем личку
            if 'username' in chat:
                name, chat_id = chat['username'], int(chat['id'])
            # Обрабатываем группы
            elif 'title' in chat:
                title, chat_id = chat['title'], int(chat['id'])
                # Просим пользователя ввести name, только если эту группу мы не знаем
                if chat_id not in self._known_chats.values() and chat_id not in new_chats.values():
                    name = str(input("[telegram] New group [{0}] detected! Please type group name:\n".format(title)))

            # Пропускаем кейсы когда отсутствует name или chat_id
            if not name or not chat_id:
                continue

            # Если чат ранее не известен - добавляем его в список новых чатов
            if chat_id not in self._known_chats.values():
                new_chats[name] = chat_id

        # Дописываем новые чаты в файл
        self.__append_new_chats_to_config(new_chats)

    def __get_updates(self) -> list:
        url = "https://api.telegram.org/bot{0}/getUpdates".format(self._token)
        response = requests.get(url=url)
        return json.loads(response.content.decode("utf-8"))["result"]

    def __append_new_chats_to_config(self, new_chats):
        # Загружаем config
        config = configparser.ConfigParser()
        config.read(self._config_file)

        # Дописываем чаты
        for k, v in new_chats.items():
            config.set("KnownChats", k, str(v))

        # Записываем в файл
        with open(self._config_file, "w") as config_file:
            config.write(config_file)
