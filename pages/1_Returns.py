import pandas as pd
import plotly.express as px
import streamlit as st

from interest_data_service import load_risk_free_rates
from market_data_service import get_prices_df
from portfolio_metrics import (
    calculate_return_bins,
    calculate_return_rates,
    calculate_arr,
    compute_excess_returns,
    compute_asset_growth_index,
    compute_portfolio_growth_index,
    compute_sharpe_ratio,
)
from utils import ensure_portfolio_configured, fig_layout


ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Returns Analysis"
"## Growth Index"

prices_df = get_prices_df(portfolio_df["ticker"].tolist())

"### Comparative Asset Performance"
"""Each asset receives 10.000 €, invested at the same time,
beginning from the newest fund's starting date."""
indv_perf_df = compute_asset_growth_index(prices_df, portfolio_df)

fig = px.line(indv_perf_df, labels={"variable": "Asset", "value": "Value"})
fig.update_layout(**fig_layout)

st.plotly_chart(fig)

"### Portfolio Performance"
"""Your portfolio receives 10.000 €, invested at the beggining from the newest fund's starting date.
The growth of the portfolio is calculated as the weighted average of the growth of each asset, according to the allocation you defined."""
portfolio_performance_df = compute_portfolio_growth_index(prices_df, portfolio_df)
fig = px.line(
    portfolio_performance_df,
    y="portfolio_value",
    labels={"portfolio_value": "Portfolio Value", "date": "Date"},
)
fig.update_layout(**fig_layout, showlegend=False)

st.plotly_chart(fig)

"## Annual Returns"
"""Your portfolio's return rate is calculated as the percentage change of the portfolio value from one year to the next."""
annual_returns_df = calculate_return_rates(
    portfolio_performance_df.resample("YE").last()["portfolio_value"]
)
monthly_returns_df = calculate_return_rates(
    portfolio_performance_df.resample("ME").last()["portfolio_value"]
)
annualized_return = calculate_arr(annual_returns_df["return"])

st.metric("Annualized Return Rate", f"{annualized_return:.2f} %", border=True)

fig = px.bar(
    annual_returns_df,
    x=annual_returns_df.index.year,
    y="return",
    color="sign",
    color_discrete_map={"positive": "green", "negative": "red"},
    labels={"return": "Annual Return Rate (%)", "x": "Year"},
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig)


"### Annual Returns Count"
annual_bins_df = calculate_return_bins(annual_returns_df["return"], bin_by=5)

fig = px.bar(
    annual_bins_df,
    x="label",
    y="count",
    color="sign",
    color_discrete_map={"positive": "green", "negative": "red"},
    labels={"count": "Number of Years", "label": "Annual Return Range (%)"},
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

"## Excess Return Rate vs Risk-Free Rate"
"""The risk-free rate used is the average 3-month Euribor rate.
The excess return rate is calculated as the difference between
the portfolio's annual return rate and the risk-free annual rate."""
monthly_risk_free_rates_df, annual_risk_free_rates_df = load_risk_free_rates()


monthly_excess_df = compute_excess_returns(
    monthly_returns_df["return"], monthly_risk_free_rates_df["rate"]
)
annual_excess_df = compute_excess_returns(
    annual_returns_df["return"], annual_risk_free_rates_df["rate"]
)

excess_period_pill = st.pills("Time period:", ["Annual", "Monthly"], default="Annual")

fig_df = annual_excess_df if excess_period_pill == "Annual" else monthly_excess_df
fig_df = fig_df.rename(
    columns={
        "portfolio_return": "Portfolio Return Rate",
        "risk_free_rate": "Risk-Free Rate",
        "excess_return_rate": "Excess Return Rate",
    }
)
fig = px.line(
    fig_df,
    x=fig_df.index,
    y=fig_df.columns,
    labels={
        "x": "Date",
        "date": "Date",
        "value": "Rate",
        "variable": "Type",
    },
)
fig.update_layout(**fig_layout)
st.plotly_chart(fig)


sharpe_ratio = compute_sharpe_ratio(monthly_excess_df)

"## Risk-Adjusted Performance"
"### Sharpe Ratio"
"The Sharpe Ratio is a measure of an investment's risk-adjusted performance,\
calculated by comparing its return to that of a risk-free asset.\
It's calculated with the following formula:"

st.latex(r"Sharpe Ratio = \frac{R_p - R_f}{\sigma_p}")

"""
Where:
 - $R_p$: return of the portfolio
 - $R_f$: risk-free rate
 - $\\sigma_p$: Standard deviation of the portfolio's excess return
 
The Sharpe Ratio is calculated from monthly excess returns."""

st.metric("Your Portfolio Sharpe Ratio", f"{sharpe_ratio:.2f}", border=True)

sharpe_table_df = pd.DataFrame(
    {
        "Sharpe Ratio": ["< 1", "1 - 1.99", "2 - 2.99", "> 3"],
        "Interpretation": [
            "Bad",
            "Adequate/good",
            "Very good",
            "Excellent",
        ],
    }
)
"Sharpe Ratio Interpretation:"
st.dataframe(sharpe_table_df, hide_index=True)
