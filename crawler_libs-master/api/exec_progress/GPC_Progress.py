import requests
import json


def get_global_project_api_action_status(transaction_id, api_key, url):
    """ Выполняем запрос к globalProjectControlProgress """
    # Формируем запрос
    data = json.dumps({"key": api_key, "id": transaction_id}).encode("utf-8")
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    try:
        http_response = requests.post(url=url, data=data, headers=headers)
    except Exception as e:
        raise Exception("Can`t get response: {0}".format(e))

    # Если действие завершино - возвращаем результат
    try:
        response = http_response.json()
        status = response['Status']
    except Exception:
        raise Exception("Unknown response format")

    if status and status == 'Finished':
        return True, response.get('Result', {'mode': None})
    else:
        return False, response.get('Result', {'mode': None})
