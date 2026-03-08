import plotly.express as px
import streamlit as st

from market_data_service import get_prices_df
from portfolio_metrics import compute_drawdown_df, compute_portfolio_growth
from utils import ensure_portfolio_configured, fig_layout

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Returns Analysis"
"## Maximum Drawdown"
"""Maximum drawdown represents the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained.
It is an indicator of downside risk over a specified time period."""

prices_df = get_prices_df(portfolio_df["ticker"].tolist()).dropna(how="any")
growth_df = compute_portfolio_growth(prices_df, portfolio_df)
drawdown_df = compute_drawdown_df(growth_df["portfolio_growth"])

fig = px.area(
    drawdown_df[["drawdown"]],
    labels={"date": "Date", "value": "Max Drawdown (%)"},
    color_discrete_sequence=["red"],
)
fig.update_layout(**fig_layout, showlegend=False)
st.plotly_chart(fig)
