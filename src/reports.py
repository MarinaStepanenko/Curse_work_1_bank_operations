import json
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable

import pandas as pd


def write_in_file(filename: str = "reports.csv" ) -> Callable:
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
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Принимает:датафрейм с транзакциями, название категории, опциональную дату.
    Если дата не передана, то берется текущая дата.
    Возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """
    if date is None:
        date = datetime.now()
        three_months_ago = date - timedelta(days=90)
    else:
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        print(date)
        three_months_ago = date - timedelta(days=90)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_df = transactions[
        (transactions["Дата операции"] <= date)
        &
        (transactions["Дата операции"] >= three_months_ago)
        &
        (transactions["Категория"] == category)
    ]
    print(filtered_df)
    category_df = filtered_df[[
        "Сумма операции с округлением",
        "Дата операции",
        "Категория"
    ]]
    return category_df
