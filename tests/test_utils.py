import json
from datetime import datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd
import pytest
from pandas.core.frame import DataFrame

from src.utils import (
    get_cards,
    get_currency,
    get_path_and_period,
    get_period,
    get_stock,
    get_time_for_greeting,
    get_top_transactions,
)


@patch("src.utils.datetime")
def test_get_time_for_greeting_morning(mock_datetime: Mock) -> None:
    mock_datetime.now.return_value = datetime(2023, 12, 10, 10, 9, 33)
    result = get_time_for_greeting()
    assert "Доброе утро" == result


@patch("src.utils.datetime")
def test_get_time_for_greeting_day(mock_datetime: Mock) -> None:
    mock_datetime.now.return_value = datetime(2023, 12, 10, 14, 9, 33)
    result = get_time_for_greeting()
    assert "Добрый день" == result


@patch("src.utils.datetime")
def test_get_time_for_greeting_evening(mock_datetime: Mock) -> None:
    mock_datetime.now.return_value = datetime(2023, 12, 10, 18, 9, 33)
    result = get_time_for_greeting()
    assert "Добрый вечер" == result


@patch("src.utils.datetime")
def test_get_time_for_greeting_night(mock_datetime: Mock) -> None:
    mock_datetime.now.return_value = datetime(2023, 12, 10, 2, 9, 33)
    result = get_time_for_greeting()
    assert "Доброй ночи" == result


@pytest.mark.parametrize(
    "date_time, date_format, expected",
    [
        (
            "2020-05-21 12:30:35",
            "%Y-%m-%d %H:%M:%S",
            ["01.05.2020 12:30:35", "21.05.2020 12:30:35"],
        ),
        (
            "21-06-2018 13:15:10",
            "%d-%m-%Y %H:%M:%S",
            ["01.06.2018 13:15:10", "21.06.2018 13:15:10"],
        ),
        (
            "12:10:2019 13:20:21",
            "%d:%m:%Y %H:%M:%S",
            ["01.10.2019 13:20:21", "12.10.2019 13:20:21"],
        ),
    ],
)
def test_get_period(date_time: str, date_format: str, expected: list) -> None:
    assert get_period(date_time, date_format) == expected


@patch("pandas.read_excel")
def test_get_path_and_period(mock_read_excel: Mock) -> None:
    mock_data = pd.DataFrame(
        {
            "Дата операции": ["01.01.2023", "15.01.2023", "01.02.2023", "15.02.2023"],
            "Сумма операции": [1000, 2000, 1500, 2500],
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
        }
    )
    mock_read_excel.return_value = mock_data
    result = get_path_and_period(
        "../data/test.xlsx", ["01.01.2023 00:00:00", "31.01.2023 23:59:59"]
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert all(result["Дата операции"] >= datetime(2023, 1, 1))
    assert all(result["Дата операции"] <= datetime(2023, 1, 31))


@patch("pandas.read_excel")
def test_get_path_and_period_no_period(mock_read_excel: Mock) -> None:
    mock_data = pd.DataFrame(
        {
            "Дата операции": ["01.01.2023", "15.01.2023", "01.02.2023", "15.02.2023"],
            "Сумма операции": [1000, 2000, 1500, 2500],
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
        }
    )
    mock_read_excel.return_value = mock_data
    result = get_path_and_period(
        "../data/test.xlsx", ["01.07.2019 00:00:00", "16.07.2019 13:15:29"]
    )
    assert len(result) == 0


def test_get_cards_success(sorted_df: DataFrame) -> None:
    assert get_cards(sorted_df) == [
        {"last digits": "5750", "total spent": 1000, "cashback": 10},
        {"last digits": "6789", "total spent": 2000, "cashback": 20},
    ]


def test_get_cards_empty(sort_df: pd.DataFrame) -> None:
    assert get_cards(sort_df) == []


def test_get_top_transactions(sorted_df: DataFrame) -> None:
    assert get_top_transactions(sorted_df, 1) == [
        {
            "date": "15.01.2023",
            "amount": 2000,
            "category": "Транспорт",
            "description": "РЖД",
        }
    ]


def test_get_top_transactions_empty_df() -> None:
    empty_df = pd.DataFrame(
        columns=[
            "Дата платежа",
            "Сумма операции с округлением",
            "Категория",
            "Описание",
        ]
    )
    result = get_top_transactions(empty_df, 5)
    assert len(result) == 0
    assert isinstance(result, list)


@patch("requests.request")
@patch("os.getenv")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_currencies": ["USD"], '
    '"user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}',
)
def test_get_currency_success(
    mock_open: Mock, mock_getenv: Mock, mock_requests_request: Mock
) -> None:
    mock_getenv.return_value = "test_api_key"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": 85.0, "query": {"from": "USD"}}
    mock_requests_request.return_value = mock_response
    result = get_currency("test.json")
    assert result == [{"currency": "USD", "rate": 85.0}]
    mock_open.assert_called_once_with("test.json", "r", encoding="utf-8")


@patch("requests.request")
@patch("os.getenv")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_currencies": ["USD", "EUR", "GBP"]}',
)
def test_multiple_currencies(mock_open, mock_getenv, mock_requests_request):
    mock_getenv.return_value = "test_key"

    # Создаем разные ответы для каждой валюты
    responses = [
        {"result": 85.0, "query": {"from": "USD"}},
        {"result": 95.0, "query": {"from": "EUR"}},
        {"result": 105.0, "query": {"from": "GBP"}},
    ]

    mock_responses = []
    for resp_data in responses:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = resp_data
        mock_responses.append(mock_resp)

    mock_requests_request.side_effect = mock_responses

    result = get_currency("test.json")

    assert result == [
        {"currency": "USD", "rate": 85.0},
        {"currency": "EUR", "rate": 95.0},
        {"currency": "GBP", "rate": 105.0},
    ]


@patch("requests.request")
@patch("os.getenv")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_currencies": ["USD"], '
    '"user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}',
)
def test_get_currency_no_connection(
    mock_open: Mock, mock_getenv: Mock, mock_requests_request: Mock
) -> None:
    mock_getenv.return_value = "test_api_key"

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = None
    mock_requests_request.return_value = mock_response
    result = get_currency("test.json")
    assert result == []
    mock_open.assert_called_once_with("test.json", "r", encoding="utf-8")


@patch("requests.request")
@patch("os.getenv")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": []}')
def test_get_currency_empty_currencies(
    mock_open: Mock, mock_getenv: Mock, mock_requests_request: Mock
) -> None:
    result = get_currency("test.json")

    assert result == []
    mock_requests_request.assert_not_called()


@patch("src.utils.TDClient")
@patch("os.getenv")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_stocks": ["AAPL", "AMZN"]}',
)
def test_get_stock_success(
    mock_open: Mock, mock_getenv: Mock, mock_td_client: Mock
) -> None:
    mock_getenv.return_value = "test_api_key"
    mock_instance = mock_td_client.return_value

    mock_responses = []
    test_prices = ["156.04", "200.89"]

    for price in test_prices:
        mock_response = Mock()
        mock_response.as_json.return_value = {"price": price}
        mock_responses.append(mock_response)
    mock_td_client.return_value = mock_instance
    mock_instance.price.side_effect = mock_responses
    result = get_stock("test.json")
    expected_results = [
        {"stock": "AAPL", "price": "156.04"},
        {"stock": "AMZN", "price": "200.89"},
    ]
    assert result == expected_results


@patch("src.utils.TDClient")
@patch("os.getenv")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_stocks": []}')
def test_get_stock_empty_stocks(
    mock_open: Mock, mock_getenv: Mock, mock_td_client: Mock
) -> None:
    mock_getenv.return_value = "test_api_key"

    result = get_stock("test.json")
    expected_results: list[dict] = []
    assert result == expected_results


@patch("builtins.open", mock_open(read_data="invalid json"))
def test_get_stock_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        get_stock("test.json")


@patch("src.utils.TDClient")
@patch("os.getenv")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_stocks": ["UNKNOWN", "NOTFOUND"]}',
)
def test_get_stock_all_symbols_invalid(mock_open, mock_getenv, mock_td_client):
    mock_getenv.return_value = "test_api_key"
    mock_instance = mock_td_client.return_value

    mock_instance.price.side_effect = Exception("Symbol not found")

    with pytest.raises(Exception, match="Symbol not found"):
        get_stock("test.json")
