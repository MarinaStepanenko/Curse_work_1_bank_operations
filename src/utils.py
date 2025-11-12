import json
import os
from datetime import datetime
from twelvedata import TDClient
import pandas as pd
import requests
from pandas import DataFrame
from dotenv import load_dotenv

load_dotenv()


def get_time_for_greeting() -> str:
    """
    Возвращает "Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи",
    в зависимости от текущего времени.
    """
    user_datetime = datetime.now()
    user_hour = user_datetime.hour
    if 5 <= user_hour <= 12:
        return "Доброе утро"
    elif 12 < user_hour <= 17:
        return "Добрый день"
    elif 17 < user_hour <= 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_period(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """
    Получает дату и формат даты, выдает список с 2 датами в заданном формате: первая с начала месяца,
    вторая, та. которую задали изначально.
    """
    dt = datetime.strptime(date_time, date_format)
    start_of_month = dt.replace(day=1)

    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S")
    ]


def get_path_and_period(path_to_file: str, date_period: list) -> DataFrame:
    """
    Принимает путь к эксель-файлу и диапазон даты(начала и конец периода), возвращает датафрейм-
    срез, только по выбранному временному периоду.
    """
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_time = datetime.strptime(date_period[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(date_period[1], "%d.%m.%Y %H:%M:%S")
    filtered_df = df[(df["Дата операции"] >= start_time) & (df["Дата операции"] <= end_date)]
    sorted_df = filtered_df.sort_values(by="Дата операции", ascending=True)
    return sorted_df


def get_cards(sorted_df: DataFrame) -> list[dict]:
    """
    Получает нужный отсортированный датафрейм и возвращает последние 4 цифры по картам с общими расходами,
    кэшбэком из этого периода.
    """
    card_spent_transactions = []
    card_sorted = sorted_df[
        [
          "Номер карты",
          "Сумма операции",
          "Кэшбэк",
          "Сумма операции с округлением"
        ]
    ]
    for index, row in card_sorted.iterrows():
        if row["Сумма операции"] < 0:
            last_digits = str(row["Номер карты"]).replace("*", "")
            total_spent = row["Сумма операции с округлением"]
            cashback = total_spent // 100
            row = {
                "last digits": last_digits,
                "total spent": total_spent,
                "cashback": cashback
            }
            card_spent_transactions.append(row)
    return card_spent_transactions

    #Если надо объединить по картам и сделать общую сумму
    # merged_cards = {}
    # for card_data in card_spent_transactions:
    #     last_digits = card_data["last digits"]
    #     if last_digits in merged_cards:
    #         merged_cards[last_digits]["total spent"] += card_data["total spent"]
    #         merged_cards[last_digits]["cashback"] += card_data["cashback"]
    #     else:
    #         merged_cards[last_digits] = {
    #             "last digits": card_data["last digits"],
    #             "total spent": card_data["total spent"],
    #             "cashback": card_data["cashback"]
    #         }
    # result = []
    # for card in merged_cards.values():
    #     result.append({
    #         "last digits": card["last digits"],
    #     "total spent": round(card["total spent"], 2),
    #         "cashback": round(card["cashback"], 2)
    #     })
    # return result


def get_top_transactions(sorted_df: DataFrame, top: int) -> list[dict]:
    """
    Получаем датайфрейм отсортированный, возвращает top транзакций по сумме платежа.
    """
    top_trans = []
    sorted_pay_df = sorted_df.sort_values(by="Сумма операции", ascending=False)
    top_transactions = sorted_pay_df.head(top)
    new_df = top_transactions[[
        "Дата платежа",
        "Сумма операции",
        "Категория",
        "Описание"
    ]]
    for index, row in new_df.iterrows():
        transaction = {
            "date": row["Дата платежа"],
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"]
        }
        top_trans.append(transaction)
    return top_trans


def get_currency(path_to_file: str) -> list[dict]:
    """
    Принимает путь к файлу json с кодировками валют и
    возвращает курс валют к ним.
    """
    currency_rates = []
    with open(path_to_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        currencies = data["user_currencies"]

        for currency in currencies:
            url = "https://api.apilayer.com/exchangerates_data/convert"


            headers = {"apikey": os.getenv("API_KEY")}
            payload = {
                "amount": 1,
                "from": currency,
                "to": "RUB",
            }
            response = requests.request("GET", url, headers=headers, params=payload)
            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                currency_code_response = result["query"]["from"]
                currency_amount = round(result["result"], 2)
                currency_rates.append({
                    "currency": currency_code_response,
                    "rate": currency_amount
                })
            else:
                print(f"Ошибка API для {currency}: {response.status_code}")
    return currency_rates


def get_stock(path_to_file: str) -> list[dict]:
    """
    Принимает путь к файлу, забирает нужные кодировки акции и делает запрос на стоимость этих акций.
    Возвращает список словарей с названием акций и цены.
    """
    stock_rates = []
    with open(path_to_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        stocks = data["user_stocks"]
        api_key = os.getenv("API_KEY_2")
        td = TDClient(apikey=api_key)

        for stock in stocks:
            price = td.price(symbol=stock).as_json()
            stock_rates.append({"stock": stock, "price": f"{round(float(price["price"]), 2)}"})
        # for stock in stocks:
        #     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY}"
        #     response = requests.get(url)
        #     status_code = response.status_code
        #     if status_code == 200:
        #         result = response.json()
        #         stock_code_response = result["Global Quote"]["01. symbol"]
        #         stock_price = round(float(result["Global Quote"]["05. price"]), 2)
        #         stock_rates.append({
        #             "stock": stock_code_response,
        #             "price": stock_price
        #         })
    return stock_rates
