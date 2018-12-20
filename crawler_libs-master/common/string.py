import re
import html


def extract_substring(s: str, regex: str) -> str:
    """ Возвращает первое вхождение regex-подстроки в строке """
    find = re.search(regex, s, re.I | re.S)
    return find.group(1) if find and find.group(1) else ''


def escape_sql(s: str, html_unescape: bool=False) -> str:
    """ Подготавливает строку для insert/update в базу данных """
    if html_unescape:
        s = html.unescape(s)
    return s.replace("'", "''")
