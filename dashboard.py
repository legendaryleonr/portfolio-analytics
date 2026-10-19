
import pandas as pd
import streamlit as st
import plotly.express as px

from analytics import (
    validate_transactions,
    calculate_holdings,
    calculate_risk,
)


# 1. Page setup
st.set_page_config(page_title="Portfolio Analytics", layout="wide")

st.title("Portfolio Analytics")
st.caption("A personal CS and Statistics project")


# 2. Load data
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
    prices_file or "data/prices.csv"
)


# 3. Validate inputs
required = {"date", "symbol", "type", "quantity", "price"}

if not required.issubset(transactions.columns):
    st.error("Transactions CSV is missing required columns.")
    st.stop()

if "date" not in prices.columns:
    st.error("Prices CSV must contain a date column.")
    st.stop()

if transactions.empty or prices.empty:
    st.error("Input files cannot be empty.")
    st.stop()

if not transactions["type"].isin(["BUY", "SELL"]).all():
    st.error("Transaction type must be BUY or SELL.")
    st.stop()

transactions["quantity"] = pd.to_numeric(
    transactions["quantity"], errors="coerce"
)

transactions["price"] = pd.to_numeric(
    transactions["price"], errors="coerce"
)

if transactions[["quantity", "price"]].isna().any().any():
    st.error("Quantity and price must be numeric.")
    st.stop()

if (transactions[["quantity", "price"]] <= 0).any().any():
    st.error("Quantity and price must be positive.")
    st.stop()

if transactions["symbol"].isna().any():
    st.error("Stock symbols cannot be missing.")
    st.stop()


# 4. Calculate holdings
try:
    transactions = validate_transactions(transactions)
except ValueError as error:
    st.error(str(error))
    st.stop()

holdings = calculate_holdings(transactions)

if (holdings < 0).any():
    st.error("One or more holdings have a negative balance.")
    st.stop()

holdings = holdings[holdings > 0]

if holdings.empty:
    st.warning("No open holdings.")
    st.stop()


# 5. Process price data
prices["date"] = pd.to_datetime(
    prices["date"], errors="coerce"
)

if prices["date"].isna().any():
    st.error("Invalid dates found in price data.")
    st.stop()

prices = prices.sort_values("date").set_index("date")

if not set(holdings.index).issubset(prices.columns):
    st.error("Prices are missing for one or more holdings.")
    st.stop()

prices = prices[holdings.index].copy()

for column in prices.columns:
    prices[column] = pd.to_numeric(
        prices[column], errors="coerce"
    )

if prices.isna().any().any() or (prices <= 0).any().any():
    st.error("Prices contain missing or invalid values.")
    st.stop()

if len(prices) < 2:
    st.error("At least two dates are needed for risk calculations.")
    st.stop()


# 6. Portfolio analytics
latest_prices = prices.iloc[-1]

market_values = holdings * latest_prices

total_value = market_values.sum()

allocation = market_values / total_value

# Simulation assumes current holdings existed throughout
# the historical price period.
portfolio_history = prices.mul(
    holdings, axis=1
).sum(axis=1)

# Reuse the tested function from analytics.py
volatility, max_drawdown = calculate_risk(
    portfolio_history
)


# 7. Display dashboard
a, b, c = st.columns(3)

a.metric(
    "Current Portfolio Value",
    f"${total_value:,.2f}"
)

b.metric(
    "Annualized Volatility",
    f"{volatility:.2%}"
)

c.metric(
    "Maximum Drawdown",
    f"{max_drawdown:.2%}"
)


# 8. Portfolio value chart
st.subheader("Portfolio Value")

st.line_chart(portfolio_history)


# 9. Asset allocation
st.subheader("Asset Allocation")

allocation_df = allocation.reset_index()
allocation_df.columns = ["Symbol", "Weight"]

fig = px.pie(
    allocation_df,
    names="Symbol",
    values="Weight",
    title="Portfolio Allocation"
)

st.plotly_chart(fig, use_container_width=True)


# 10. Current holdings
st.subheader("Current Holdings")

holdings_df = pd.DataFrame({
    "Shares": holdings,
    "Latest Price": latest_prices,
    "Market Value": market_values,
    "Weight": allocation
})

st.dataframe(
    holdings_df,
    use_container_width=True
)


# 11. Limitations
st.caption(
    "Uses sample data by default. Historical portfolio values "
    "assume current holdings were held throughout the price "
    "period. Risk metrics are based on this hypothetical "
    "buy-and-hold portfolio, not actual transaction timing. "
    "Excludes fees, dividends, cash balances, and cash-flow effects."
)
