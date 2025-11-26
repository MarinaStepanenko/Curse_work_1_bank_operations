import pandas as pd

from src.reports import spending_by_category
from src.services import analyze_cashback
from src.utils import get_top_transactions
from src.views import main_page

if __name__ == "__main__":
    date_user = "2020-06-03 12:30:30"
    print(main_page(date_user))

    services = analyze_cashback("data/operations.xlsx", 2018, 5)
    print(services)
    df = pd.read_excel("data/operations.xlsx", sheet_name="Отчет по операциям")
    print(get_top_transactions(df, 3))
    reports = spending_by_category(df, "Фастфуд", "2020-06-03 12:30:30")

    print(reports)
