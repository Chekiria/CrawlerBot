import os


def get_system_info() -> dict:
    """ Возвращает информацию об ОС """
    return {'os': os.name}


def change_cur_work_dir(_file_):
    """ Меняет рабочую директорию """
    os.chdir(os.path.dirname(os.path.abspath(_file_)))
