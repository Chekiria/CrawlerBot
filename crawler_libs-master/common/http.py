import requests
import urllib3
urllib3.disable_warnings()

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/52.0.2743.116 Safari/537.36"
DEFAULT_TIMEOUT = 30


def get_response(url: str, user_agent: str=DEFAULT_USER_AGENT, timeout: int=DEFAULT_TIMEOUT,
                 additional_headers: dict=None, proxies: dict=None, allow_redirects=True) -> dict:
    """ Выполянет GET-запрос к урлу, возвращает данные ответа в виде словаря """
    headers = {'User-Agent': user_agent}
    if additional_headers:
        for k, v in additional_headers.items():
            headers[k] = v

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=timeout, proxies=proxies,
                                allow_redirects=allow_redirects)
        response.encoding = 'utf-8'
    except Exception as e:
        return {}

    return {'status_code': int(response.status_code), 'end_url': response.url, 'data': response.text}


def extract_domain(url: str) -> str:
    """ Возвращает домен урла """
    import re
    find = re.search("https?://(?:www\\.)?([^/?#:]+)", url, re.I | re.S)
    return find.group(1) if find and find.group(1) else ''


def get_ip() -> str:
    """ Возвращает внешний IP """
    resp = get_response(url="https://api.ipify.org/")
    return resp["data"] if resp else ''
