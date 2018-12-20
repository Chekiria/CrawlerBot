Для вывода цветных логов нужно установить colorlog
# pip install colorlog

Создание объекта:
file_path: str(default=None)                    - Если задаём название файла логи начнут записыватся в файл. Причём
                                                уровень записываемых сообщений и формат настраивается в файле .ini
re_write: bool(default=True)                    - Перезаписывание файла логов. По умолчанию True. Если False - логи будут
                                                дописыватся. Файл не будет перезатиратся
settings_path:str(default=logger/Logger.ini)    - Путь к файлу config. По умолчанию используется файл в папке с Logger.py
                                                Файл по умолчанию уже имеет настроеный формат сообщений

Пример:
def write():
    """ Выводим логи на экран. Данная функция может быть импортирована с другого модуля"""
    import logging
    logging.debug("Hi")  # Только выводится на экран
    logging.info("Hi")  # Выводится на экран и записывается в файл
    logging.warning("Hi") # Выводится на экран и записывается в файл
    logging.error("Hi") # Выводится на экран и записывается в файл
    logging.critical("Hi") # Выводится на экран и записывается в файл


if __name__ == "__main__":
    from logger import Logger
    Logger(file_path="log1.txt")  # Логи будут записыватся в файл log1.txt в корень проекта
    write()
    write()

    Logger(file_path="log2.txt", re_write=False)  # Логи не будут перезатиратся при новом запуске скрипта
    write()
    write()
