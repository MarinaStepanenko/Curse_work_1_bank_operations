import json
import logging

from config import BASE_DIR
from src.utils import (
    get_cards,
    get_currency,
    get_path_and_period,
    get_period,
    get_stock,
    get_time_for_greeting,
    get_top_transactions,
)

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    BASE_DIR + "/logs/views.log", encoding="utf-8", mode="w"
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main_page(date_user: str) -> str:
    """
    Набор функций и главная функция, принимающая на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    """
    #  1. Приветствие
    greeting = get_time_for_greeting()
    logger.info("Программа выводит приветствие.")
    time_period = get_period(date_user)
    sorted_df = get_path_and_period("data/operations.xlsx", time_period)
    logger.info("Программа подготавливает файл.")

    # 2. По каждой карте
    cards = get_cards(sorted_df)
    logger.info("Программа формирует информацию по картам.")

    # 3. Топ 5 транзакций
    top_transactions = get_top_transactions(sorted_df, 5)
    logger.info("Программа обрабатывает топовые транзакции.")

    # 4. Курс валют
    currency = get_currency("data/user_settings.json")
    logger.info("Программа обрабатывает валюты.")

    # 5. Стоимость акций из S&P500.
    stock = get_stock("data/user_settings.json")
    logger.info("Программа обрабатывает стоимость акций.")

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rate": currency,
        "stock_prices": stock,
    }
    data_json = json.dumps(data, ensure_ascii=False, indent=4)
    logger.info("Программа подготавливает финальный запрос.")

    return data_json
