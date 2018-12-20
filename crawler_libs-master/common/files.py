import json
import os
import re


def write_json(data, fp: str, encoding: str="utf-8"):
    """ Записывает данные в формате JSON в файл """
    with open(fp, 'wt', encoding=encoding) as w:
        w.write(json.dumps(data, ensure_ascii=False, indent=4))


def read_json(fp: str, encoding: str="utf-8"):
    """ Читает данные из файла в формате JSON """
    return json.load(open(fp, 'rt', encoding=encoding))


def get_folder_files(fp: str) -> list:
    """ Возвращает список файлов, которые находятся в папке fp """
    r_files = list()
    for root, dirs, files in os.walk(fp.rstrip('/'), topdown=True):
        r_files = ["{0}/{1}".format(root, file) for file in files]
        break
    return r_files


def create_folder(fp):
    """ Создает папку, если такой не существует """
    if not os.path.exists(fp):
        os.makedirs(fp)


def write_tsv(data: list, fp: str, encoding: str="utf-8"):
    """ Записывает данные в формате TSV(колонки через табуляцию) в файл """
    if isinstance(data[0], list) or isinstance(data[0], tuple):
        data = [tuple(map(lambda x: re.sub("\s{2,}|\t|\n", " ", str(x).replace("None", "")), item)) for item in data]
        result = '\n'.join(['\t'.join(item) for item in data])
    else:
        data = list(map(lambda x: re.sub("\s{2,}|\t|\n", " ", str(x).replace("None", "")), data))
        result = '\n'.join(data) + '\n'

    with open(fp, 'wt', encoding=encoding) as file:
        file.write(result)


def read_tsv(fp: str, encoding: str="utf-8") -> list:
    """ Читает данные из файла в формате TSV(колонки через табуляцию) """
    with open(fp, 'rt', encoding=encoding) as file:
        data = file.read().strip()

    # Получаем список строк
    data = data.split('\n')

    # Если в файле только 1 колонка
    if len(data[0].split('\t')) == 1:
        return data
    else:
        return list(map(lambda x: tuple(x.split('\t')), data))
