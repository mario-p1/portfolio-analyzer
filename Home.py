import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_analyzer.market_data_service import get_prices_df, get_ticker_details
from portfolio_analyzer.metrics import calculate_return_rates, compute_portfolio_growth
from portfolio_analyzer.utils import (
    load_value,
    rename_ticker_columns_to_names,
    store_value,
)

"# Portfolio Analyzer"
"## Disclaimer"
"""This project is a **experimental tool** created for learning and demonstration purposes.

**It is not intended for production use or real financial decision-making.**

The models and results provided may be simplified and are not guaranteed to be accurate.
Use at your own risk.
"""

"## Overview"
"""
Portfolio Analyzer helps you assess your portfolio's risk and return.

Start by configuring your portfolio: enter the tickers of your assets and their allocations.
Next, explore the tabs on the left sidebar to analyze performance and risk.
Use Monte Carlo simulations to forecast future performance and optimize your portfolio composition.
"""

"# Portfolio Configuration"
"""
Configure your portfolio by entering its assets and their allocations.
All analyses and results throughout the app will use this setup.

- **Ticker**: Enter each asset's ticker symbol (Yahoo Finance format, e.g., `AAPL`, `IUSQ.DE`).
Separate multiple tickers with semicolons (`;`).
- **Allocation**: Specify the percentage of your portfolio allocated to each asset.
The total allocation across all assets must sum to 100%.
"""

if "tickers" not in st.session_state.to_dict():
    st.session_state["tickers"] = "IUSQ.DE;EUNL.DE;IUSN.DE;EUNM.DE"
    st.session_state["allocation_IUSQ.DE"] = 50
    st.session_state["allocation_EUNL.DE"] = 30
    st.session_state["allocation_IUSN.DE"] = 10
    st.session_state["allocation_EUNM.DE"] = 10


load_value("tickers")
st.text_input(
    "Tickers (separated by ';')",
    key="_tickers",
    on_change=store_value,
    args=["tickers"],
)

portfolio_items = []
for i, item in enumerate(st.session_state.tickers.split(";")):
    try:
        ticker_data = get_ticker_details(item)
        portfolio_items.append({"ticker": item, **ticker_data})
    except Exception as e:
        st.error(e)
        st.stop()

portfolio_df = pd.DataFrame.from_dict(portfolio_items)
columns = st.columns(2)

for item in portfolio_df.itertuples():
    col = columns[item.Index % 2]
    with col:
        load_value(f"allocation_{item.ticker}")
        st.number_input(
            f"Allocation of '{item.ticker}' (%)",
            min_value=0,
            max_value=100,
            key=f"_allocation_{item.ticker}",
            on_change=store_value,
            args=[f"allocation_{item.ticker}"],
        )
        store_value(f"allocation_{item.ticker}")

portfolio_df["allocation"] = portfolio_df["ticker"].map(
    lambda ticker: st.session_state[f"allocation_{ticker}"]
)

if portfolio_df["allocation"].sum() != 100:
    st.error(
        f"Sum of allocation accross all assets must be 100, current sum is: {portfolio_df['allocation'].sum()}"
    )
    st.stop()


st.session_state["portfolio_df"] = portfolio_df

"# Portfolio Summary"
"## Asset Allocation"
"""The pie chart below shows the allocation of your portfolio across different assets."""

# portfolio pie chart
fig = px.pie(portfolio_df, values="allocation", names="name", hole=0.3)
fig.update_traces(textinfo="label+percent")
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

"## Asset Correlations"
prices_df = get_prices_df(portfolio_df["ticker"].tolist())

monthly_prices_df = prices_df.resample("ME").last()

portfolio_growth_df = compute_portfolio_growth(
    monthly_prices_df, portfolio_df, normalize_value=10_000
).round(0)

indv_growth_df = portfolio_growth_df[portfolio_df["ticker"]]
indv_growth_df = rename_ticker_columns_to_names(indv_growth_df, portfolio_df)

for col in indv_growth_df.columns:
    indv_growth_df[col] = calculate_return_rates(indv_growth_df[col])["return"]

corr_df = indv_growth_df.corr()

fig = px.imshow(corr_df)

st.plotly_chart(fig)
