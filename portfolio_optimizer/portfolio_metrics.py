from datetime import datetime
import streamlit as st

import pandas as pd

from utils import rename_ticker_columns_to_names


def compute_asset_growth_index(
    prices_df: pd.DataFrame, portfolio_df: pd.DataFrame
) -> pd.DataFrame:
    indv_growth_df = prices_df.dropna(how="any")
    indv_growth_df = rename_ticker_columns_to_names(indv_growth_df, portfolio_df)
    indv_growth_df = (indv_growth_df * 10_000 / indv_growth_df.iloc[0]).round(0)

    return indv_growth_df


def compute_portfolio_growth_index(
    prices_df: pd.DataFrame, portfolio_df: pd.DataFrame
) -> pd.DataFrame:
    portfolio_growth_df = prices_df.dropna(how="any")

    allocation = (portfolio_df.set_index("ticker")["allocation"] / 100).sort_values(
        ascending=True
    )
    portfolio_growth_df = (
        (portfolio_growth_df * allocation).sum(axis=1).to_frame(name="portfolio_value")
    )

    portfolio_growth_df = (
        portfolio_growth_df * 10_000 / portfolio_growth_df.iloc[0]
    ).round(0)

    return portfolio_growth_df


def calculate_return_rates(
    value_series: pd.Series, current_year: int = datetime.now().year
) -> pd.DataFrame:
    return_rates_df = (value_series.pct_change().dropna() * 100).to_frame(name="return")

    return_rates_df = return_rates_df[return_rates_df.index.year < current_year]

    return_rates_df["sign"] = (
        return_rates_df["return"].ge(0).map({True: "positive", False: "negative"})
    )

    return return_rates_df


def calculate_return_bins(return_rates_series: pd.Series, bin_by: int) -> pd.DataFrame:
    min_annual_return = int(return_rates_series.min() / bin_by - 1) * bin_by
    max_annual_return = int(return_rates_series.max() / bin_by + 1) * bin_by

    bin_region = max(abs(min_annual_return), abs(max_annual_return))

    bins = list(range(-bin_region, bin_region + bin_by, bin_by))

    annual_bins = (
        pd.cut(return_rates_series, bins=bins, labels=bins[:-1])
        .value_counts()
        .sort_index()
        .to_frame()
        .reset_index(names="return_bin_left")
    )

    annual_bins["sign"] = (
        annual_bins["return_bin_left"].ge(0).map({True: "positive", False: "negative"})
    )
    annual_bins["label"] = annual_bins["return_bin_left"].map(
        lambda x: f"{x} to {x + bin_by} %"
    )

    return annual_bins


def compute_excess_returns(
    return_series: pd.Series,
    interest_rate_series: pd.Series,
    current_year: int = datetime.now().year,
) -> pd.DataFrame:
    excess_returns_df = return_series.to_frame(name="portfolio_return")
    excess_returns_df["risk_free_rate"] = interest_rate_series
    excess_returns_df["excess_return_rate"] = (
        excess_returns_df["portfolio_return"] - excess_returns_df["risk_free_rate"]
    )
    excess_returns_df = excess_returns_df[excess_returns_df.index.year < current_year]
    return excess_returns_df


def compute_sharpe_ratio(annual_rates_df: pd.DataFrame) -> float:
    return (
        annual_rates_df["excess_return_rate"].mean()
        / annual_rates_df["excess_return_rate"].std()
    )


def calculate_arr(return_series: pd.Series) -> float:
    """Annualized Return Rate"""
    n_years = len(return_series)
    return ((1 + return_series.div(100)).prod() ** (1 / n_years) - 1) * 100
