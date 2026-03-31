import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_analyzer.interest_data_service import load_risk_free_rates
from portfolio_analyzer.market_data_service import get_prices_df
from portfolio_analyzer.metrics import (
    bin_series,
    calculate_arr,
    calculate_return_rates,
    compute_excess_returns,
    compute_portfolio_growth,
    compute_sharpe_ratio,
)
from portfolio_analyzer.utils import (
    ensure_portfolio_configured,
    fig_layout,
    rename_ticker_columns_to_names,
)

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Returns Analysis"
"""
This page breaks down your portfolio's historical growth, annual returns,
and overall risk-adjusted performance.
It compares your gains against risk-free rates to calculate your Sharpe ratio,
and maps out asset correlations to show exactly how your investments move together.
"""
"## Growth Index"
"""
To ensure a fair comparison, this chart tracks a hypothetical 10,000 € investment
in each individual asset, starting simultaneously from the inception date of the newest fund.
"""

prices_df = get_prices_df(portfolio_df["ticker"].tolist())

monthly_prices_df = prices_df.resample("ME").last()

portfolio_growth_df = compute_portfolio_growth(
    monthly_prices_df, portfolio_df, normalize_value=10_000
).round(0)

"### Comparative Asset Performance"
"""Each asset receives 10.000 €, invested at the same time,
beginning from the newest fund's starting date."""

indv_growth_df = portfolio_growth_df[portfolio_df["ticker"]]


fig = px.line(
    rename_ticker_columns_to_names(indv_growth_df, portfolio_df),
    labels={"variable": "Asset", "value": "Value"},
)
fig.update_layout(**fig_layout)

st.plotly_chart(fig)

"### Portfolio Performance"
"""
This chart illustrates the growth of a 10,000 € initial investment
in your overall portfolio.
The total value is calculated using the weighted average of your
assets based on your defined allocation."""
portfolio_performance_df = portfolio_growth_df[["portfolio_growth"]]
fig = px.line(
    portfolio_performance_df,
    y="portfolio_growth",
    labels={"portfolio_growth": "Portfolio Value", "date": "Date"},
)
fig.update_layout(**fig_layout, showlegend=False)

st.plotly_chart(fig)

"## Annual Returns"
"""
Review your year-over-year performance.
This section tracks the annual percentage change in your portfolio's total value,
helping you identify long-term trends and volatility.
"""
annual_returns_df = calculate_return_rates(
    portfolio_performance_df.resample("YE").last()["portfolio_growth"]
)
monthly_returns_df = calculate_return_rates(
    portfolio_performance_df.resample("ME").last()["portfolio_growth"]
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
"""
This chart groups your historical returns into specific percentage ranges,
giving you a clear visual breakdown of how often your portfolio
experiences different levels of gains or losses.
"""
annual_bins_df = bin_series(
    annual_returns_df["return"], bin_by=5, label_suffix=" %", cutoff_bins=False
)

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
"""
We use the average 3-month Euribor as our baseline risk-free rate.
Your excess return shows the exact difference between your portfolio's
actual gains and this baseline, revealing how much value your
investment strategy is adding over a safe asset.

You can toggle between annual and monthly views to analyze this performance across different timeframes.
"""
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
"""
The Sharpe Ratio is the gold standard for measuring risk-adjusted performance.
It helps you understand if your portfolio's returns are
truly compensating you for the level of volatility you're enduring.

Mathematically, it measures your excess return per unit of risk:
"""

st.latex(r"Sharpe Ratio = \frac{R_p - R_f}{\sigma_p}")

"""
Where:
 - $R_p$: Return of your portfolio
 - $R_f$: Risk-free rate
 - $\\sigma_p$: Standard deviation of your portfolio's excess return (volatility)
 
*Note: Your Sharpe Ratio below is calculated using your monthly excess returns.*
"""

# st.metric("Your Portfolio Sharpe Ratio", f"{sharpe_ratio:.2f}", border=True)

sharpe_table_df = pd.DataFrame(
    {
        "start": [-1, 1, 2, 3],
        "end": [1, 2, 3, 5],
        "interpretation": [
            "Bad",
            "Adequate/good",
            "Very good",
            "Excellent",
        ],
        "color": ["red", "orange", "lightgreen", "green"],
    }
)
sharpe_table_df["center"] = (sharpe_table_df["start"] + sharpe_table_df["end"]) / 2
sharpe_table_df["width"] = sharpe_table_df["end"] - sharpe_table_df["start"]


# sharpe_ratio = 1.5
fig = go.Figure(
    data=go.Bar(
        x=sharpe_table_df["center"],
        width=sharpe_table_df["width"],
        y=[1] * 4,
        marker_color=sharpe_table_df["color"],
        text=sharpe_table_df["interpretation"],
        insidetextanchor="middle",
    ),
)
fig.add_vline(x=sharpe_ratio, line_width=3, line_dash="dash", line_color="white")
fig.add_annotation(
    x=sharpe_ratio,
    y=1,
    text=f"Your Sharpe Ratio: {sharpe_ratio:.2f}",
    font=dict(color="black", size=16),
)
fig.update_yaxes(visible=False)
fig.update_layout(height=350)

st.plotly_chart(fig)

"## Returns Correlations"
"""
Correlation reveals the underlying relationships between your investments.
It shows whether your assets tend to rise and fall together (high correlation)
or move independently (low correlation). 

Mixing assets that don't move in lockstep is the key to smoothing out volatility,
reducing your overall risk, and building a truly diversified portfolio.
"""
indv_returns_df = indv_growth_df.copy()
indv_returns_df = rename_ticker_columns_to_names(indv_returns_df, portfolio_df, "name")
for col in indv_returns_df.columns:
    indv_returns_df[col] = calculate_return_rates(indv_returns_df[col])["return"]

corr_df = indv_returns_df.corr()

fig = px.imshow(corr_df, zmin=-1, zmax=1)
fig.update_xaxes(tickangle=30)
fig.update_layout(height=500)

st.plotly_chart(fig)
