import json
import logging

import pandas as pd

from config import BASE_DIR

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    BASE_DIR + "/logs/services.log", encoding="utf-8", mode="w"
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def analyze_cashback(path_to_file: str, year: int, month: int) -> str:
    """
    Анализирует выгодные категории кэшбэка. Возвращает json
    """
    logger.info(
        f"Информация о транзакциях была выгружена из excel файла {path_to_file}."
    )
    df = pd.read_excel(path_to_file)
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    filtered_df = df[
        (df["Дата операции"].dt.year == year)
        & (df["Дата операции"].dt.month == month)
        & (df["Кэшбэк"] > 0)
    ]

    cashback_by_category = filtered_df.groupby("Категория")["Кэшбэк"].sum()
    logger.info(f"Кэшбэк был суммирован для каждой категории в {cashback_by_category}.")

    result_dict = {}
    for category, cashback in cashback_by_category.items():
        result_dict[f"{category}"] = cashback
        logger.info(f"Информация по кэшбэку записывается в json {result_dict}.")

    return json.dumps(result_dict, ensure_ascii=False, indent=4)
