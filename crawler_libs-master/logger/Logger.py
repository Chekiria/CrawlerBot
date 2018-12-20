import logging


class Logger:
    def __init__(self, file_path: str=None, re_write: bool=True, settings_path: str=__file__.replace('.py', '.ini')):
        self.__fp, self.__re_write, self.__s_fp = file_path, re_write, settings_path

        self.__root = logging.root
        self.__create_logger()

    def __remove_previous_handlers(self):
        """ Чистим предыдущие настройки """
        self.__root.handlers.clear()

    def __create_logger(self):
        """ Настраиваем логгер """
        self.__remove_previous_handlers()
        self.__root.setLevel(logging.DEBUG)

        f_settings, c_settings = self.__get_settings()
        self.__get_console_handler(c_settings)
        self.__get_file_handler(f_settings)

        for log in self.__root.manager.loggerDict.keys():
            logger = self.__root.manager.loggerDict[log]
            logger.disabled = True

    def __get_file_handler(self, f_settings):
        """ Настраиваем запись логов в файл """
        if not self.__fp:
            return

        msg_format, dt_format, log_lvl = f_settings
        msg_formatter = logging.Formatter(msg_format, dt_format)

        f_mode = "wt" if self.__re_write is True else 'a'
        handler = logging.FileHandler(self.__fp, f_mode, 'utf-8')
        handler.setLevel(log_lvl)
        handler.setFormatter(msg_formatter)

        self.__root.addHandler(handler)

    def __get_console_handler(self, c_settings):
        """ Настраиваем вывод логов на экран """
        msg_format, dt_format, log_lvl = c_settings
        try:
            import colorlog
            msg_formatter = colorlog.ColoredFormatter(msg_format, dt_format)
        except:
            msg_formatter = logging.Formatter(msg_format.replace("%(log_color)s", ""))

        handler = logging.StreamHandler()
        handler.setLevel(log_lvl)
        handler.setFormatter(msg_formatter)

        self.__root.addHandler(handler)

    def __get_settings(self):
        """ Получаем данные с конфига """
        import configparser
        config = configparser.ConfigParser()

        config.read(self.__s_fp)
        f_msg_format = config.get("File", "message_format", raw=True)
        f_dt_format = config.get("File", "dt_format", raw=True)
        f_log_lvl = config.get("File", "log_lvl")

        c_msg_format = config.get("Console", "message_format", raw=True)
        c_dt_format = config.get("Console", "dt_format", raw=True)
        c_log_lvl = config.get("Console", "log_lvl")

        return (f_msg_format, f_dt_format, f_log_lvl), (c_msg_format, c_dt_format, c_log_lvl)
