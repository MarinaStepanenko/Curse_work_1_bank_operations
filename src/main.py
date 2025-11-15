import pandas as pd

from src.reports import spending_by_category
from src.services import analyze_cashback
from src.views import main_page
from pprint import pprint

if __name__ == "__main__":
    # date_user = "2020-06-03 12:30:30"
    # pprint(main_page(date_user))
    #
    # services = analyze_cashback("../data/operations.xlsx", 2018, 5)

    df = pd.read_excel("../data/operations.xlsx", sheet_name="Отчет по операциям")

    reports = spending_by_category(df, "Фастфуд", "2020-06-03 12:30:30") # проблема тут даем дату год-месяц-день в процессе меняет месяц и день местами. визуально
    print(reports)