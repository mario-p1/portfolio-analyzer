import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from market_data_service import get_prices_df
from portfolio_metrics import (
    compute_portfolio_growth,
)
from utils import (
    ensure_portfolio_configured,
    fig_layout,
    rename_ticker_columns_to_names,
)
from scipy.stats import norm

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Portfolio Forecast"
"""Use Monte Carlo Simulation to forecast the future performance of your portfolio,
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

days = 360
num_simulations = 1_000

start_value = np.repeat(10_000, num_simulations).reshape(-1, 1)

returns = norm.rvs(loc=mean, scale=std, size=(num_simulations, days))

forecast = start_value * (1 + returns).cumprod(axis=1)
forecast = np.hstack([start_value, forecast])

"## Monte Carlo Simulation"
fig = px.line(
    forecast[:50].T,
    labels={"index": "Days", "value": "Simulated Portfolio Value"},
)
fig.update_layout(**{**fig_layout, "showlegend": False, "hovermode": None})
st.plotly_chart(fig)
