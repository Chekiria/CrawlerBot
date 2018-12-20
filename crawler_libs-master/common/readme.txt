В либе собраны все часто используемые функции

## Пример использования:
from common import extract_domain, write_json, get_ip

my_public_link = get_ip()
print(my_public_link)

url = "https://www.wbg-erfurt.de/unsere-genossenschaft/karriere/"
domain = extract_domain(url=url)
print(domain)

data = {"key": "value"}
write_json(fp="data.json", data=data)
