from datetime import timedelta
from unittest.mock import patch

import pandas as pd
from datetime import datetime

from src.reports import spending_by_category, write_in_file


@write_in_file()
def func_div() -> pd.DataFrame:
    return pd.DataFrame({"Номер карты": ["*5750", "*6789"]})


def test_write_in_file() -> None:
    func_div()
    result_df = pd.read_csv("data/reports.csv")
    expected_df = pd.DataFrame(
        {
            "Номер карты": ["*5750", "*6789"],
        }
    )
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_spending_by_category(reports_df) -> None:
    expected_df = pd.DataFrame(
        {
            "Сумма операции с округлением": [1000],
            "Дата операции": pd.to_datetime(["2023-01-01 16:14:10"]),
            "Категория": ["Еда"],
        }
    )
    with patch("src.reports.write_in_file") as mock_write:
        mock_write.return_value = pd.read_csv("data/reports.csv")
        result_df = spending_by_category(reports_df, "Еда", "2023-01-01 16:14:10")
        pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=False)


def test_spending_by_category_fake_now(reports_df) -> None:
    with patch("src.reports.write_in_file") as mock_write:
        mock_write.return_value = lambda x: x
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 11, 10, 15, 20, 10)
            result_df = spending_by_category(reports_df, "Транспорт")
            result_df["Дата операции"] = pd.to_datetime(result_df["Дата операции"])
            three_month_ago = datetime(2025, 11, 10) - timedelta(days=90)
            assert (
                pd.to_datetime(["2025-10-10 15:20:21"])
                in result_df["Дата операции"].values
            )
            assert pd.to_datetime(["2025-10-10 15:20:21"]) >= three_month_ago
