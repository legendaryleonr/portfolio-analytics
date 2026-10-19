
import pandas as pd
import pytest

from analytics import (
    calculate_holdings,
    calculate_risk,
    validate_transactions,
)
from performance import calculate_performance


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


def test_rejects_overselling():
    transactions = pd.DataFrame({
        "date": ["2026-07-01", "2026-07-02"],
        "symbol": ["AAPL", "AAPL"],
        "type": ["BUY", "SELL"],
        "quantity": [5, 10],
        "price": [180, 190],
    })

    with pytest.raises(ValueError):
        validate_transactions(transactions)


def test_contributions_do_not_count_as_returns():
    prices = pd.DataFrame(
        {"AAPL": [100.0, 110.0, 110.0]},
        index=pd.to_datetime([
            "2026-07-01",
            "2026-07-02",
            "2026-07-03",
        ]),
    )

    transactions = pd.DataFrame({
        "date": ["2026-07-01", "2026-07-02"],
        "symbol": ["AAPL", "AAPL"],
        "type": ["BUY", "BUY"],
        "quantity": [1, 1],
        "price": [100, 110],
    })

    result = calculate_performance(transactions, prices)

    assert result["portfolio_value"].iloc[-1] == 220
    assert result["return_index"].iloc[-1] == pytest.approx(110)
