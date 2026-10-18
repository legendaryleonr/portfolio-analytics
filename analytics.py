import numpy as np
import pandas as pd


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