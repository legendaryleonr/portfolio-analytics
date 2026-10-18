import pandas as pd
import pytest

from analytics import calculate_holdings, calculate_risk


def test_holdings():
    transactions = pd.DataFrame({
        "symbol": ["AAPL", "AAPL", "MSFT"],
        "type": ["BUY", "SELL", "BUY"],
        "quantity": [10, 3, 5],
    })

    result = calculate_holdings(transactions)

    assert result["AAPL"] == 7
    assert result["MSFT"] == 5


def test_risk():
    prices = pd.Series([100, 110, 99])

    volatility, max_drawdown = calculate_risk(prices)

    assert volatility > 0
    assert max_drawdown == pytest.approx(-0.10)