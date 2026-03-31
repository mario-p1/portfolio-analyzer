import plotly.express as px
import streamlit as st
import pandas as pd

from portfolio_analyzer.market_data_service import get_prices_df
from portfolio_analyzer.metrics import (
    compute_drawdown_df,
    compute_portfolio_growth,
    compute_value_at_risk,
)
from portfolio_analyzer.utils import ensure_portfolio_configured, fig_layout

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Risks Analysis"
"""
This page breaks down your portfolio's exposure to downside risk and potential losses.
It visualizes your historical maximum drawdown to highlight worst-case drops,
and calculates your Value at Risk (VaR) to project the maximum expected
monthly and annual losses at specific confidence levels.
"""
"## Maximum Drawdown"
"""
Maximum drawdown measures the steepest historical decline from a **portfolio's peak**
to its **lowest trough** before recovering.
It serves as a primary indicator of worst-case downside risk.
"""

with st.expander("How to Interpret This Chart"):
    """
    A drawdown of 0% means the portfolio is at an all-time high. 
    Any drop below 0% shows how much the portfolio has lost from that peak. 
    The 'Maximum Drawdown' is the lowest point on this chart.
    """

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
"""
Value at Risk (VaR) represents the maximum expected
loss over a specified time period at a given confidence level. 

For example, an annual VaR at a 95% confidence level means there is only a 5%
chance your portfolio will lose more than that amount in a given year.
"""

with st.expander("View Calculation Methodology"):
    """
    We calculate VaR using the variance-covariance method, which assumes returns are normally distributed. 
    The annual VaR is estimated by scaling the monthly VaR.
    
    The monthly VaR is computed as:
    """
    st.latex(r"VaR_{monthly} = \mu - z \cdot \sigma")

    """and the annual VaR is estimated as:"""
    st.latex(r"VaR_{annual} = 12 \cdot \mu - \sqrt{12} \cdot z \cdot \sigma")

    r"""
    where:
    - $\mu$ is the mean of the monthly returns
    - $\sigma$ is the standard deviation of the monthly returns
    - $z$ is the z-score corresponding to the confidence level (e.g., 95% or 99%)
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

monthly_var_df = pd.DataFrame(
    {
        "Confidence Level": ["95%", "99%"],
        "Monthly VaR (%)": [var_monthly_95, var_monthly_99],
    }
)
annual_var_df = pd.DataFrame(
    {
        "Confidence Level": ["95%", "99%"],
        "Annual VaR (%)": [var_annual_95, var_annual_99],
    }
)

left_col, right_col = st.columns(2)

with left_col:
    "### Monthly Value at Risk"
    fig = px.bar(
        monthly_var_df,
        x="Confidence Level",
        y="Monthly VaR (%)",
        color="Confidence Level",
        color_discrete_map={"95%": "orange", "99%": "red"},
    )
    fig.update_traces(texttemplate="%{y:.2f}%", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

with right_col:
    "### Annual Value at Risk"
    fig = px.bar(
        annual_var_df,
        x="Confidence Level",
        y="Annual VaR (%)",
        color="Confidence Level",
        color_discrete_map={"95%": "orange", "99%": "red"},
    )
    fig.update_traces(texttemplate="%{y:.2f}%", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
