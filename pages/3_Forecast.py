import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import norm

from market_data_service import get_prices_df
from portfolio_metrics import (
    bin_series,
    compute_portfolio_growth,
)
from utils import ensure_portfolio_configured, fig_layout

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Forecast"
"""Uses Monte Carlo Simulation to forecast the future performance of your portfolio,
based on the historical returns of its assets."""


prices_df = get_prices_df(portfolio_df["ticker"].tolist())
portfolio_growth_df = compute_portfolio_growth(prices_df, portfolio_df)

daily_returns_df = portfolio_growth_df.pct_change().dropna(how="any")

mean = daily_returns_df["portfolio_growth"].mean()
std = daily_returns_df["portfolio_growth"].std()


left_col, right_col = st.columns(2)
with left_col:
    st.metric("Mean daily return", f"{mean:.4%}", border=True)
with right_col:
    st.metric("Standard deviation of daily returns", f"{std:.4%}", border=True)

days = st.session_state["days_slider"] if "days_slider" in st.session_state else 180
num_simulations = 10_000
start_value = 10_000

start_values = np.repeat(start_value, num_simulations).reshape(-1, 1)

returns = norm.rvs(loc=mean, scale=std, size=(num_simulations, days))

forecast = start_values * (1 + returns).cumprod(axis=1)
forecast = np.hstack([start_values, forecast])

"## Monte Carlo Simulation"
f"""The Monte Carlo simulation was performed by simulating {num_simulations} possible future
paths of the portfolio value over the next {days} days,
based on the historical mean and standard deviation of daily returns.

For practical purposes, only 25 simulated paths are shown in the plot below.
"""

st.slider(
    "Days to Forecast",
    min_value=30,
    max_value=360,
    value=days,
    key="days_slider",
    step=10,
)

fig = px.line(
    forecast[:10, :].T,
    labels={"index": "Days", "value": "Simulated Portfolio Value"},
)
fig.update_layout(**{**fig_layout, "showlegend": False, "hovermode": False})
st.plotly_chart(fig)

final_day_forecast = pd.DataFrame({"value": forecast[:, -1]})
final_day_forecast["sign"] = final_day_forecast["value"].apply(
    lambda x: "positive" if x >= 10_000 else "negative"
)

"## Forecasted Portfolio Value Distribution"
f"""Distribution of the simulated portfolio values at the end of the forecast period (day {days})."""
left_col, right_col = st.columns(2)
with left_col:
    st.metric(
        "Expected Value Mean", f"{final_day_forecast['value'].mean():.0f}", border=True
    )
with right_col:
    st.metric(
        "Expected Value Standard Deviation",
        f"{final_day_forecast['value'].std():.0f}",
        border=True,
    )

final_bins = bin_series(
    final_day_forecast["value"], bin_by=1_000, sign_threshold=start_value
)

fig = px.bar(
    final_bins,
    x="label",
    y="count",
    color="sign",
    color_discrete_map={"positive": "green", "negative": "red"},
    labels={
        "count": "Number of Simulations",
        "label": "Simulated Portfolio Value Range",
    },
)

fig.update_layout(**{**fig_layout, "showlegend": False, "bargap": 0.2})
st.plotly_chart(fig)
