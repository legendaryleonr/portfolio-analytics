
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Portfolio Analytics", layout="wide")

st.title("Portfolio Analytics")
st.caption("A personal CS and Statistics project")

# 1. Load data
transactions_file = st.file_uploader(
    "Upload transactions CSV", type="csv"
)
prices_file = st.file_uploader(
    "Upload daily prices CSV", type="csv"
)

transactions = pd.read_csv(
    transactions_file or "data/transactions.csv"
)
prices = pd.read_csv(
    prices_file or "data/prices.csv",
    parse_dates=["date"],
)

if "date" in prices.columns:
    prices["date"] = pd.to_datetime(prices["date"])

# 2. Validate inputs
required = {"symbol", "type", "quantity", "price"}

if not required.issubset(transactions.columns):
    st.error("Transactions CSV is missing required columns.")
    st.stop()

if not {"date"}.issubset(prices.columns):
    st.error("Prices CSV must contain a date column.")
    st.stop()

if not transactions["type"].isin(["BUY", "SELL"]).all():
    st.error("Transaction type must be BUY or SELL.")
    st.stop()

if (transactions[["quantity", "price"]] <= 0).any().any():
    st.error("Quantity and price must be positive.")
    st.stop()

# 3. Calculate holdings
transactions["signed_qty"] = np.where(
    transactions["type"] == "BUY",
    transactions["quantity"],
    -transactions["quantity"],
)

holdings = transactions.groupby("symbol")["signed_qty"].sum()

if (holdings < 0).any():
    st.error("One or more holdings have a negative balance.")
    st.stop()

holdings = holdings[holdings > 0]

if holdings.empty:
    st.warning("No open holdings.")
    st.stop()

prices = prices.sort_values("date").set_index("date")

if not set(holdings.index).issubset(prices.columns):
    st.error("Prices are missing for one or more holdings.")
    st.stop()

prices = prices[holdings.index]

if prices.isna().any().any() or (prices <= 0).any().any():
    st.error("Prices contain missing or invalid values.")
    st.stop()

latest_prices = prices.iloc[-1]
market_values = holdings * latest_prices

# 4. Portfolio analytics
total_value = market_values.sum()
allocation = market_values / total_value

# Buy-and-hold simulation using current holdings.
# This is NOT a cash-flow-adjusted historical return.
portfolio_history = prices.mul(holdings, axis=1).sum(axis=1)
daily_returns = portfolio_history.pct_change().dropna()

volatility = daily_returns.std() * np.sqrt(252)
running_peak = portfolio_history.cummax()
drawdown = portfolio_history / running_peak - 1
max_drawdown = drawdown.min()

# 5. Display dashboard
a, b, c = st.columns(3)

a.metric("Current Portfolio Value", f"${total_value:,.2f}")
b.metric("Annualized Volatility", f"{volatility:.2%}")
c.metric("Maximum Drawdown", f"{max_drawdown:.2%}")

st.subheader("Portfolio Value")
st.line_chart(portfolio_history)

st.subheader("Asset Allocation")

allocation_df = allocation.reset_index()
allocation_df.columns = ["Symbol", "Weight"]

fig = px.pie(
    allocation_df,
    names="Symbol",
    values="Weight",
    title="Portfolio Allocation",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Current Holdings")

holdings_df = pd.DataFrame({
    "Shares": holdings,
    "Latest Price": latest_prices,
    "Market Value": market_values,
    "Weight": allocation,
})

st.dataframe(holdings_df, use_container_width=True)

st.caption(
    "Uses sample data by default. Historical chart assumes "
    "current holdings were held throughout the price period. "
    "Excludes fees, dividends, cash balances, and cash-flow effects."
)
