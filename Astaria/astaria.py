import fake_useragent
import json
import requests

input("Нажмите Enter")
proxies_txt = input("Перетяните txt файл с прокси, в формате user:pass@ip:port: ")
mails_txt = input("Перетащите файл с почтами: ")
print()

def get_mails():
    with open(mails_txt, encoding="utf-8") as file:
        for i in file:
            yield i
data_mails = get_mails()

def get_proxies():
    with open(proxies_txt, encoding="utf-8") as file:
        for i in file:
            yield i
data_proxies = get_proxies()

with open("errors mails.txt", "w", encoding="utf-8") as file:
    file.seek(0)
errorscount = 0
successcount = 0

def main():
    with open("errors mails.txt", "w", encoding="utf-8") as file:
        for i in get_mails():
            headers = {
                "user-agent": fake_useragent.UserAgent().random
            }
            proxies = {
                "http": f"http://{next(data_proxies)[:-1]}"
            }
            url = f"https://xyz.us11.list-manage.com/subscribe/post-json?u=7ba25d0a2461b4e360ab05a54&amp;id=9c1bff8a37&EMAIL={i[:-2]}&c=__jp0"
            response = requests.get(url, headers=headers, proxies=proxies)
            if json.loads(response.content.decode('utf-8')[6:-1])["result"] == "error":
                file.write(i)
                global errorscount
                errorscount += 1
            elif json.loads(response.content.decode('utf-8')[6:-1])["result"] == "success":
                global successcount
                successcount += 1

print("")
print("=" * 50)
print(f"Зарегистрировано почт: {successcount} | Кол-во ошибок: {errorscount}\n")
print(f'Почты, которые вызвали ошибки сохранены в "errors mails.txt"')
print("="*50)
input("Завершить Enter")
