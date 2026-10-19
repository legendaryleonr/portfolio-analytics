
import numpy as np
import pandas as pd


def validate_transactions(transactions):
    required = {"symbol", "type", "quantity", "price", "date"}

    if not required.issubset(transactions.columns):
        raise ValueError("Missing required transaction columns")

    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if df["date"].isna().any():
        raise ValueError("Invalid transaction date")

    if df["symbol"].isna().any():
        raise ValueError("Missing stock symbol")

    if not df["type"].isin(["BUY", "SELL"]).all():
        raise ValueError("Transaction must be BUY or SELL")

    for column in ["quantity", "price"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

        if df[column].isna().any() or (df[column] <= 0).any():
            raise ValueError(f"Invalid {column}")

    df = df.sort_values("date", kind="stable")

    holdings = {}

    for _, row in df.iterrows():
        symbol = row["symbol"]
        quantity = row["quantity"]

        current = holdings.get(symbol, 0)

        if row["type"] == "BUY":
            holdings[symbol] = current + quantity
        else:
            if quantity > current:
                raise ValueError(
                    f"Cannot sell more {symbol} shares than owned"
                )
            holdings[symbol] = current - quantity

    return df


def calculate_holdings(transactions):
    signed = np.where(
        transactions["type"] == "BUY",
        transactions["quantity"],
        -transactions["quantity"],
    )

    return (
        transactions.assign(signed_qty=signed)
        .groupby("symbol")["signed_qty"]
        .sum()
    )


def calculate_risk(portfolio_history):
    returns = portfolio_history.pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)

    peak = portfolio_history.cummax()
    max_drawdown = (portfolio_history / peak - 1).min()

    return volatility, max_drawdown
