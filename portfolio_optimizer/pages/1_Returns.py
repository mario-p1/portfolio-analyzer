import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_optimizer.interest_data_service import load_risk_free_rates
from portfolio_optimizer.market_data_service import get_prices_df
from portfolio_optimizer.portfolio_metrics import (
    bin_annual_returns,
    calculate_annual_returns,
    calculate_arr,
    compute_annual_excess_returns,
    compute_asset_growth_index,
    compute_portfolio_growth_index,
    compute_sharpe_ratio,
)
from portfolio_optimizer.utils import fig_layout


# Load state
if "portfolio_df" not in st.session_state:
    st.error("Please go to the 'Configuration' page to configure your portfolio.")
    st.stop()
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
annual_returns_df = calculate_annual_returns(portfolio_performance_df)
annualized_return = calculate_arr(annual_returns_df)

st.metric("Annualized Return Rate", f"{annualized_return:.2f} %", border=True)

fig = px.bar(
    annual_returns_df,
    x=annual_returns_df.index.year,
    y="annual_return",
    color="sign",
    color_discrete_map={"positive": "green", "negative": "red"},
    labels={"annual_return": "Annual Return Rate (%)", "x": "Year"},
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig)


"### Annual Returns Count"
annual_bins_df = bin_annual_returns(annual_returns_df, bin_by=5)

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
interest_rates_df = load_risk_free_rates()
annual_excess_returns_df = compute_annual_excess_returns(
    annual_returns_df, interest_rates_df
)

fig_df = (
    annual_excess_returns_df[
        ["portfolio_return", "risk_free_annual_rate", "excess_return_rate"]
    ].rename(
        columns={
            "portfolio_return": "Portfolio Return Rate",
            "risk_free_annual_rate": "Risk-Free Annual Rate",
            "excess_return_rate": "Excess Return Rate",
        }
    )
    * 100
)
fig = px.line(
    fig_df,
    x=fig_df.index.year,
    y=fig_df.columns,
    labels={
        "x": "Year",
        "value": "Rate",
        "variable": "Type",
    },
)
fig.update_layout(**fig_layout)
st.plotly_chart(fig)


sharpe_ratio = compute_sharpe_ratio(annual_excess_returns_df)

"## Risk-Adjusted Performance"
"### Sharpe Ratio"
"The Sharpe Ratio is a measure of an investment's risk-adjusted performance,\
calculated by comparing its return to that of a risk-free asset.\
It's calculated with the following formula:"

st.latex(r"Sharpe Ratio = \frac{R_p - R_f}{\sigma_p}")

"Where:"
" - $R_p$: return of the portfolio"
" - $R_f$: risk-free rate"
" - $\sigma_p$: Standard deviation of the portfolio's excess return"
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
