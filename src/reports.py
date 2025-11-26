import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from pandas import Series

from config import BASE_DIR

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)

os.chdir(Path(__file__).parent.parent)

file_handler = logging.FileHandler(
    BASE_DIR + "/logs/reports.log", encoding="utf-8", mode="w"
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def write_in_file(filename: str = "reports.csv") -> Callable:
    """
    Декоратор должен принимать аргумент filename,
    который определяет, куда будет записываться датафрейм из отчета:
    Если filename задан, логи записываются в указанный файл.Если filename не задан,
    используем файл по умолчанию.
    """

    def decorator(func: Callable) -> Any:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            filepath = f"data/{filename}"
            os.makedirs("data", exist_ok=True)
            result.to_csv(filepath, index=False, date_format="%d.%m.%Y %H:%M:%S")
            return result

        return wrapper

    return decorator


@write_in_file()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> Series | Any:
    """
    Принимает:датафрейм с транзакциями, название категории, опциональную дату.
    Если дата не передана, то берется текущая дата.
    Возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """
    if date is None:
        date = datetime.now()
        logger.info("Кэшбэк по категории за 3 месяца будет рассчитан от текущей даты.")

        three_months_ago = date - timedelta(days=90)
    else:
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        logger.info(f"Кэшбэк по категории за 3 месяца будет рассчитан от даты {date}.")

        three_months_ago = date - timedelta(days=90)
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], dayfirst=True
    )
    filtered_df = transactions[
        (transactions["Дата операции"] <= date)
        & (transactions["Дата операции"] >= three_months_ago)
        & (transactions["Категория"] == category)
    ]

    category_df = filtered_df[
        ["Сумма операции с округлением", "Дата операции", "Категория"]
    ]
    logger.info("Кэшбэк по категории за 3 месяца записывается в результат.")

    return category_df
