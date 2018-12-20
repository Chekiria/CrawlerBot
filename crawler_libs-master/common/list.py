import pandas


def sum_col(lst: list, col: int=0) -> int:
    """ Возвращает сумму указанной колонки """
    summa = 0
    for row in lst:
        summa += int(row[col])
    return summa


def sort_by_col(lst: list, col: int=0, desc: bool=True):
    """ Сортирует список по указанной колонке """
    lst.sort(key=lambda i: i[col], reverse=desc)


def drop_duplicates(data: list) -> list:
    """ Удаляем дубликаты из списка. Возвращаем записи в том же формате (регистр, пробелы в начале / конце),
            в котором они пришли к функции
    При этом считаются дубликатами записи в разных регистрах, с пробельными символами в начале / конце
    Примеры 1)"test" и "Test" - дубликаты; 2)"test" и " test" - дубликаты; 3)"test" и "test1" - Не дубликаты
    """
    if not isinstance(data[0], int) and not isinstance(data[0], str):
        raise TypeError("Can`t drop duplicate. Must be list of str or int")

    # Создаём dataframe на 2 колонки с одинаковыми данными
    df = pandas.DataFrame(list(zip(data, data)), columns=['one', 'two'], dtype=object)

    # Вторую колонку переводим в нижний регистр и убираем пробльные символы в начале/конце
    df['two'] = df['two'].str.lower().str.strip()

    # Удаляем дубликаты, возвращаем результат
    df = df.drop_duplicates(subset='two')
    return df['one'].tolist()
