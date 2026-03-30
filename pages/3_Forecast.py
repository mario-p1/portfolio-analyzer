import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import norm

from portfolio_analyzer.market_data_service import get_prices_df
from portfolio_analyzer.metrics import (
    bin_series,
    compute_portfolio_growth,
)
from portfolio_analyzer.utils import ensure_portfolio_configured, fig_layout

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Forecast"
"""
This tool uses a Monte Carlo simulation to project your portfolio's future value,
drawing on the historical daily returns of your selected assets

Explore the distribution of these past returns below, and adjust
the forecast timeframe to visualize potential future paths.
"""

"## Daily Returns Distribution"
"""
This chart visualizes the distribution of your historical daily returns,
overlaid with the fitted normal curve that powers the forecast.
"""

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

bin_region = daily_returns_df["portfolio_growth"].quantile(0.999) * 100

daily_bins_df = (
    pd.cut(
        daily_returns_df["portfolio_growth"] * 100,
        # bins=50,
        bins=np.arange(-bin_region, bin_region, 0.1),
    )
    .value_counts()
    .sort_index()
    .to_frame(name="count")
    .reset_index(names="bin")
)


normal_dist_df = pd.DataFrame(
    {"value": norm.rvs(loc=mean * 100, scale=std * 100, size=10_000)}
)


normal_dist_bins = (
    pd.cut(normal_dist_df["value"], bins=daily_bins_df["bin"].cat.categories)
    .value_counts()
    .sort_index()
    .to_frame(name="count")
    .reset_index(names="bin")
)


fig = px.bar(
    x=daily_bins_df["bin"].apply(lambda x: x.mid),
    y=daily_bins_df["count"] / daily_bins_df["count"].sum(),
    labels={"x": "Daily Return", "y": "Frequency"},
    color_discrete_sequence=["orange"],
)
fig.update_traces(name="Historical Returns", showlegend=True)
fig.add_scatter(
    x=normal_dist_bins["bin"].apply(lambda x: x.mid),
    y=normal_dist_bins["count"] / normal_dist_bins["count"].sum(),
    mode="markers",
    line={"color": "black", "shape": "spline", "smoothing": 1.3},
    name="Fitted Normal Distribution",
)
fig.update_layout(**fig_layout, showlegend=True)
st.plotly_chart(fig)


"## Monte Carlo Simulation"

days = st.session_state["days_slider"] if "days_slider" in st.session_state else 180
num_simulations = 10_000
start_value = 10_000

start_values = np.repeat(start_value, num_simulations).reshape(-1, 1)

returns = norm.rvs(loc=mean, scale=std, size=(num_simulations, days))

forecast = start_values * (1 + returns).cumprod(axis=1)
forecast = np.hstack([start_values, forecast])

f"""The Monte Carlo simulation was performed by simulating {num_simulations} possible future
paths of the portfolio value over the next {days} days,
based on the historical mean and standard deviation of daily returns.

For practical purposes, only 20 simulated paths are shown in the plot below.
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
    forecast[:20, :].T,
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
