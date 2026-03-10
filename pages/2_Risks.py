import math

import plotly.express as px
import streamlit as st

from market_data_service import get_prices_df
from portfolio_metrics import compute_drawdown_df, compute_portfolio_growth
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

"## Value at Risk (VaR)"
"""Value at Risk (VaR) represent maximum expected loss over a specified time period at a given confidence level.
"""

monthly_prices_df = prices_df.resample("ME").last()
monthly_growth_df = compute_portfolio_growth(monthly_prices_df, portfolio_df)
monthly_growth_df["monthly_return"] = monthly_growth_df["portfolio_growth"].pct_change()

st.write(monthly_growth_df)

# TODO: Check formulas
var_95 = (
    12 * monthly_growth_df["monthly_return"].mean()
    - math.sqrt(12) * 1.645 * monthly_growth_df["monthly_return"].std()
) * 100
var_99 = (
    12 * monthly_growth_df["monthly_return"].mean()
    - math.sqrt(12) * 2.33 * monthly_growth_df["monthly_return"].std()
) * 100

left_col, right_col = st.columns(2)
with left_col:
    st.metric(
        label="VaR (95%)",
        value=f"{var_95:.2f} %",
    )
with right_col:
    st.metric(
        label="VaR (99%)",
        value=f"{var_99:.2f} %",
    )
