import json

import pandas as pd


def analyze_cashback(path_to_file: str, year: int, month: int) -> str:
    """
    Анализирует выгодные категории кэшбэка. Возвращает json
    """
    df = pd.read_excel(path_to_file)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered_df = df[
        (df["Дата операции"].dt.year == year)
        &
        (df["Дата операции"].dt.month == month)
        &
        (df["Кэшбэк"] > 0)
    ]

    cashback_by_category = filtered_df.groupby("Категория")["Кэшбэк"].sum()
    result_dict = {}
    for category, cashback in cashback_by_category.items():
        result_dict["Категория"] = cashback

    return json.dumps(result_dict, ensure_ascii=False, indent=4)
