import json
from typing import Any

from src.utils import (get_time_for_greeting, get_period, get_path_and_period,
                       get_cards, get_top_transactions, get_currency, get_stock)


def main_page(date_user: str) -> dict[str, Any]:
    """
    Набор функций и главная функция, принимающая на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    """
    #  1. Приветствие
    greeting = get_time_for_greeting()
    time_period = get_period(date_user)
    sorted_df = get_path_and_period("../data/operations.xlsx", time_period)

    # 2. По каждой карте
    cards = get_cards(sorted_df)

    # 3. Топ 5 транзакций
    top_transactions = get_top_transactions(sorted_df, 5)

    # 4. Курс валют
    currency = get_currency("../data/user_settings.json")

    # 5. Стоимость акций из S&P500.
    stock = get_stock("../data/user_settings.json")
    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rate": currency,
        "stock_prices": stock
    }
    data_json = json.dumps(data, ensure_ascii=False, indent=4)
    return data_json
