import json
from unittest.mock import Mock, patch

import pandas as pd

from src.services import analyze_cashback


@patch("pandas.read_excel")
def test_analyze_cashback_success(mock_read_excel: Mock) -> None:
    mock_data = pd.DataFrame(
        {
            "Дата операции": [
                "01.01.2023 13:20:25",
                "15.01.2023 13:20:25",
                "01.02.2023 13:10:20",
                "15.02.2023 13:10:20",
            ],
            "Сумма операции": [1000, 2000, 1500, 2500],
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
            "Кэшбэк": [15, 12, 5, 10],
        }
    )
    mock_read_excel.return_value = mock_data
    result = analyze_cashback("test.xlsx", 2023, 2)
    expected_dict = {"Еда": 5, "Развлечения": 10}
    dict_json = json.dumps(expected_dict, ensure_ascii=False, indent=4)
    assert isinstance(result, str)
    assert result == dict_json


@patch("pandas.read_excel")
def test_analyze_cashback_empty_dict(mock_read_excel: Mock) -> None:
    mock_data = pd.DataFrame(
        {
            "Дата операции": [
                "01.01.2023 13:20:25",
                "15.01.2023 13:20:25",
                "01.02.2023 13:10:20",
                "15.02.2023 13:10:20",
            ],
            "Сумма операции": [1000, 2000, 1500, 2500],
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
            "Кэшбэк": [15, 12, 5, 10],
        }
    )
    mock_read_excel.return_value = mock_data
    result = analyze_cashback("test.xlsx", 2018, 4)
    expected_dict: dict[str, str] = {}
    dict_json = json.dumps(expected_dict, ensure_ascii=False, indent=4)
    assert isinstance(result, str)
    assert result == dict_json


@patch("pandas.read_excel")
def test_analyze_cashback_correct_format(mock_read_excel: Mock) -> None:
    mock_data = pd.DataFrame(
        {
            "Дата операции": [
                "01.05.2023 13:20:25",
                "15.01.2023 13:20:25",
                "01.02.2023 13:10:20",
                "15.02.2023 13:10:20",
            ],
            "Сумма операции": [1000, 2000, 1500, 2500],
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
            "Кэшбэк": [15, 12, 5, 10],
        }
    )
    mock_read_excel.return_value = mock_data
    result = analyze_cashback("test.xlsx", 2023, 1)

    assert "    " in result
    assert '"Транспорт"' in result
