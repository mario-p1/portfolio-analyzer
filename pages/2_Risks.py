import math

import plotly.express as px
import streamlit as st

from market_data_service import get_prices_df
from portfolio_metrics import (
    compute_drawdown_df,
    compute_portfolio_growth,
    compute_value_at_risk,
)
from utils import ensure_portfolio_configured, fig_layout

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Risks Analysis"
"## Maximum Drawdown"
"""Maximum drawdown represents the maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained.
It is an indicator of downside risk over a specified time period."""

prices_df = get_prices_df(portfolio_df["ticker"].tolist()).dropna(how="any")
growth_df = compute_portfolio_growth(prices_df, portfolio_df)
drawdown_df = compute_drawdown_df(growth_df["portfolio_growth"])

fig = px.area(
    drawdown_df[["drawdown"]],
    labels={"date": "Date", "value": "Maximum Drawdown (%)"},
    color_discrete_sequence=["red"],
)
fig.update_layout(**fig_layout, showlegend=False)
st.plotly_chart(fig)

"## Maximum Loss (Value at Risk)"
"""Value at Risk (VaR) represent maximum expected loss over a specified time
period at a given confidence level.

We calculate annual VaR at the 95% and 99% confidence levels
using the variance-covariance method, which assumes that returns are normally
distributed.

At a 95% or 99% confidence level, VaR means there is a 5% or 1% chance
that the portfolio will lose more than this amount in a year.

The annual VaR is estimated by scaling the monthly VaR.

The VaR is computed using the following formula:
"""
st.latex(r"VaR_{monthly} = \mu -  z \cdot \sigma")

"""and the annual VaR is estimated as:"""
st.latex(r"VaR_{annual} = 12 \cdot \mu - \sqrt{12} \cdot z \cdot \sigma")

"""where:
- $\\mu$ is the mean of the monthly returns
- $\\sigma$ is the standard deviation of the monthly returns
- $z$ is the z-score corresponding to the confidence level
"""

monthly_prices_df = prices_df.resample("ME").last()
monthly_growth_df = compute_portfolio_growth(monthly_prices_df, portfolio_df)
monthly_growth_df["monthly_return"] = monthly_growth_df["portfolio_growth"].pct_change()


var_monthly_95 = compute_value_at_risk(
    monthly_growth_df["monthly_return"], confidence_level=0.95
)

var_monthly_99 = compute_value_at_risk(
    monthly_growth_df["monthly_return"], confidence_level=0.99
)

var_annual_95 = compute_value_at_risk(
    monthly_growth_df["monthly_return"], confidence_level=0.95, scale=12
)
var_annual_99 = compute_value_at_risk(
    monthly_growth_df["monthly_return"], confidence_level=0.99, scale=12
)

left_col, right_col = st.columns(2)
with left_col:
    st.metric(
        label="Monthly VaR (95%)",
        value=f"{var_monthly_95:.2f} %",
        border=True,
    )
with right_col:
    st.metric(
        label="Monthly VaR (99%)",
        value=f"{var_monthly_99:.2f} %",
        border=True,
    )

left_col, right_col = st.columns(2)
with left_col:
    st.metric(
        label="Annual VaR (95%)",
        value=f"{var_annual_95:.2f} %",
        border=True,
    )
with right_col:
    st.metric(
        label="Annual VaR (99%)",
        value=f"{var_annual_99:.2f} %",
        border=True,
    )
