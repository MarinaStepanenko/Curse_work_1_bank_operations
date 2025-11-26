import json
from unittest.mock import Mock, patch

from src.views import main_page


@patch("src.views.get_stock")
@patch("src.views.get_currency")
@patch("src.views.get_top_transactions")
@patch("src.views.get_cards")
@patch("src.views.get_path_and_period")
@patch("src.views.get_period")
@patch("src.views.get_time_for_greeting")
@patch("src.views.logger")
def test_main_page_success(
    mock_logger: Mock,
    mock_get_time_for_greeting: Mock,
    mock_get_period: Mock,
    mock_get_path_and_period: Mock,
    mock_get_cards: Mock,
    mock_get_top_transactions: Mock,
    mock_get_currency: Mock,
    mock_get_stock: Mock,
) -> None:
    mock_get_time_for_greeting.return_value = "Доброй ночи"
    mock_get_period.return_value = ["05.12.2023 15:24:10", "10.05.2023 14:10:29"]
    mock_get_path_and_period.return_value = Mock()
    mock_get_cards.return_value = [
        {"last digits": "5750", "total spent": 1000, "cashback": 10}
    ]
    mock_get_top_transactions.return_value = [
        {
            "date": "15.01.2023",
            "amount": 2000,
            "category": "Транспорт",
            "description": "РЖД",
        }
    ]
    mock_get_currency.return_value = [{"currency": "EUR", "rate": 75.12}]
    mock_get_stock.return_value = [
        {"stock": "AAPL", "price": "156.04"},
        {"stock": "AMZN", "price": "200.89"},
    ]

    result = main_page("2020-06-03 12:30:30")
    data = json.loads(result)
    assert isinstance(result, str)
    assert data["greeting"] == "Доброй ночи"
    assert data["cards"][0]["last digits"] == "5750"
    assert data["currency_rate"][0]["currency"] == "EUR"
    assert data["stock_prices"][1]["price"] == "200.89"

    assert mock_logger.info.call_count >= 6
