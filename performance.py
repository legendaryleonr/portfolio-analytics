
import pandas as pd


def calculate_performance(transactions, prices):
    """
    Transactions execute at the daily closing price.
    Purchases and sales occur after that day's price movement.
    Cash flows are excluded from investment returns.
    """
    trades = transactions.copy()
    trades["date"] = pd.to_datetime(trades["date"])

    prices = prices.sort_index()

    if prices.empty or prices.index.has_duplicates:
        raise ValueError("Prices must have unique dates")

    if not set(trades["symbol"]).issubset(prices.columns):
        raise ValueError("Missing price columns")

    if not trades["date"].isin(prices.index).all():
        raise ValueError("Transaction dates must match price dates")

    shares = pd.Series(0.0, index=prices.columns)
    previous_prices = None
    portfolio_index = 100.0

    records = []

    for day, current_prices in prices.iterrows():

        # Return earned by shares held overnight
        if previous_prices is not None:
            starting_value = (shares * previous_prices).sum()

            if starting_value > 0:
                gain = (
                    shares * (current_prices - previous_prices)
                ).sum()

                daily_return = gain / starting_value
            else:
                daily_return = 0.0

            portfolio_index *= (1 + daily_return)

        # Apply today's trades after the daily price movement
        todays_trades = trades[trades["date"] == day]

        for _, trade in todays_trades.iterrows():
            symbol = trade["symbol"]
            quantity = float(trade["quantity"])

            if trade["type"] == "BUY":
                shares[symbol] += quantity
            else:
                shares[symbol] -= quantity

        portfolio_value = (shares * current_prices).sum()

        records.append({
            "date": day,
            "portfolio_value": portfolio_value,
            "return_index": portfolio_index,
        })

        previous_prices = current_prices.copy()

    return pd.DataFrame(records).set_index("date")
