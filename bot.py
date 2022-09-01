import string
import random
import re
from random import randrange
from datetime import timedelta, date
from datetime import datetime
import time
import json
from twocaptcha import TwoCaptcha
from config import api_key_for_2captcha
import requests
from config import list_proxy


class DiscordBot:

    proxy_for_2captcha = list_proxy[random.randint(0, len(list_proxy)-1)]
    proxy_for_requests = "http://" + proxy_for_2captcha + "/"

    @staticmethod
    def generate_new_random_proxy() -> None:
        DiscordBot.proxy_for_2captcha = list_proxy[random.randint(0, len(list_proxy) - 1)]

    @staticmethod
    def generate_password(len_password: int) -> str:
        lowercase = list(string.ascii_lowercase)
        uppercase = list(string.ascii_uppercase)
        letters = list(string.digits)
        password = ""
        for i in range(len_password):
            random_number_for_type_symbol = random.randint(1, 3)
            if random_number_for_type_symbol == 1:
                random_symbol = lowercase[random.randint(0, len(lowercase)-1)]
            elif random_number_for_type_symbol == 2:
                random_symbol = uppercase[random.randint(0, len(uppercase)-1)]
            else:
                random_symbol = letters[random.randint(0, len(letters)-1)]
            password = password + random_symbol
        return password

    @staticmethod
    def validate_email(email: str) -> bool:
        if type(email) is not str:
            return False
        if len(email) < 7 or len(email) > 100:
            return False
        if re.search("^[a-zA-Z0-9]+@[a-zA-Z0-9]{4,}\.[a-zA-Z0-9]{2,}$", email) is None:
            return False
        return True

    @staticmethod
    def validate_nickname(nickname: str) -> bool:
        if type(nickname) is not str:
            return False
        if len(nickname) < 3 or len(nickname) > 50:
            return False
        if re.search("^[a-zA-Z0-9]+$", nickname) is None:
            return False
        return True

    @staticmethod
    def random_datetime(start: datetime, end: datetime) -> datetime:
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return start + timedelta(seconds=random_second)

    @staticmethod
    def solve_captcha():

        print("--start solving captcha--")

        sitekey = "4c672d35-0701-42b2-88c3-78380b0db560"

        solver = TwoCaptcha(api_key_for_2captcha)
        result = solver.hcaptcha(sitekey=sitekey, url="https://discord.com/register",
                                 proxy={'type': 'HTTP', 'uri': DiscordBot.proxy_for_2captcha})

        balance = solver.balance()

        captcha_id = result['captchaId']
        if result.get("code") is not None:
            key = result.get("code")
        else:
            time.sleep(20)
            key = solver.get_result(captcha_id)

        print("balance=", balance)
        print("key=", key)
        return key

    @staticmethod
    def main(email: str, nickname: str) -> None:

        d1 = datetime.strptime('1/1/1940 1:30 PM', '%m/%d/%Y %I:%M %p')
        d2 = datetime.strptime('1/1/2005 4:50 AM', '%m/%d/%Y %I:%M %p')
        date_of_birth = DiscordBot.random_datetime(d1, d2).date()
        password = DiscordBot.generate_password(8)

        print("proxy=", DiscordBot.proxy_for_2captcha)
        key = DiscordBot.solve_captcha()

        if DiscordBot.sent_request_for_creating_account(key, date_of_birth, email, password, nickname):
            time.sleep(5)
            DiscordBot.sent_request_to_login_and_get_token(email, password)

    @staticmethod
    def sent_request_for_creating_account(key, date_of_birth: date, email: str, password: str, nickname: str) -> bool:

        proxies = {
            "http": DiscordBot.proxy_for_requests
        }

        url = "https://discord.com/api/v9/experiments"
        response = requests.get(url=url, proxies=proxies).json()

        fingerprint = response['fingerprint']

        body = {
            "captcha_key": key,
            "consent": True,
            "date_of_birth": str(date_of_birth),
            "email": email,
            "gift_code_sku_id": None,
            "invite": None,
            "password": password,
            "promotional_email_opt_in": False,
            "username": nickname,
            "fingerprint": fingerprint
        }

        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "uk-UA,uk;q=0.9",
            "content-length": str(len(json.dumps(body))),
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": "https://discord.com/register",
            "sec-ch-ua": 'Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/104.0.0.0 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "uk",
            "x-fingerprint": fingerprint
        }

        print("--sending request for creating account--")
        print("body=", body)
        url = "https://discord.com/api/v9/auth/register"
        response = requests.post(url=url, json=body, headers=headers, proxies=proxies)
        if response.status_code != 201:
            print("error, status_code=", response.status_code)
            print("response=", response.text)
            return False
        print("success")
        print("response=", response.text)
        return True

    @staticmethod
    def sent_request_to_login_and_get_token(login: str, password: str) -> bool:

        print("--sending request for login--")
        proxies = {
            "http": DiscordBot.proxy_for_requests
        }

        url = "https://discord.com/api/v9/experiments"
        response = requests.get(url=url, proxies=proxies).json()

        fingerprint = response['fingerprint']

        body = {
            "captcha_key": None,
            "login": login,
            "gift_code_sku_id": None,
            "login_source": None,
            "password": password,
            "undelete": False
        }

        headers = {
            "accept": "*/*",
            #"accept-encoding": "gzip, deflate, br", # with this error load to json
            "accept-language": "uk-UA,uk;q=0.9",
            "content-length": str(len(json.dumps(body))),
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": "https://discord.com/login",
            "sec-ch-ua": 'Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/104.0.0.0 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "uk",
            "x-fingerprint": fingerprint
        }

        url = "https://discord.com/api/v9/auth/login"
        response = requests.post(url=url, json=body, headers=headers, proxies=proxies)
        if response.status_code != 200:
            print("error, status_code=", response.status_code)
            print("response=", response.text)
            return False
        print("success")
        print("json with auth_token=", json.loads(response.text))
        return True


