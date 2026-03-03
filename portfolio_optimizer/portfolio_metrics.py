from datetime import datetime

import pandas as pd

from portfolio_optimizer.utils import rename_ticker_columns_to_names


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


def bin_annual_returns(annual_returns_df: pd.DataFrame, bin_by: int) -> pd.DataFrame:
    min_annual_return = (
        int(annual_returns_df["annual_return"].min() / bin_by - 1) * bin_by
    )
    max_annual_return = (
        int(annual_returns_df["annual_return"].max() / bin_by + 1) * bin_by
    )

    bin_region = max(abs(min_annual_return), abs(max_annual_return))

    bins = list(range(-bin_region, bin_region + bin_by, bin_by))

    annual_bins = (
        pd.cut(annual_returns_df["annual_return"], bins=bins, labels=bins[:-1])
        .value_counts()
        .sort_index()
        .to_frame()
        .reset_index()
    )

    annual_bins["sign"] = (
        annual_bins["annual_return"].ge(0).map({True: "positive", False: "negative"})
    )
    annual_bins["label"] = annual_bins["annual_return"].map(
        lambda x: f"{x} to {x + bin_by} %"
    )

    return annual_bins


def compute_annual_excess_returns(
    annual_returns_df: pd.DataFrame,
    interest_rates_df: pd.DataFrame,
    current_year: int = datetime.now().year,
) -> pd.DataFrame:
    annual_rates_df = annual_returns_df.copy().rename(
        columns={"annual_return": "portfolio_return"}
    )
    annual_rates_df["portfolio_return"] = annual_rates_df["portfolio_return"].div(100)

    annual_rates_df = annual_rates_df.join(interest_rates_df, how="inner").dropna()
    annual_rates_df["excess_return_rate"] = (
        annual_rates_df["portfolio_return"] - annual_rates_df["risk_free_annual_rate"]
    )

    annual_rates_df = annual_rates_df[annual_rates_df.index.year < current_year]

    return annual_rates_df


def compute_sharpe_ratio(annual_rates_df: pd.DataFrame) -> float:
    return (
        annual_rates_df["excess_return_rate"].mean()
        / annual_rates_df["excess_return_rate"].std()
    )


def calculate_annual_returns(
    portfolio_performance_df: pd.DataFrame, current_year: int = datetime.now().year
) -> pd.DataFrame:
    annual_returns_df = (
        portfolio_performance_df.resample("YE").last().pct_change().dropna() * 100
    )
    annual_returns_df.columns = ["annual_return"]

    annual_returns_df = annual_returns_df[annual_returns_df.index.year < current_year]

    annual_returns_df["sign"] = (
        annual_returns_df["annual_return"]
        .ge(0)
        .map({True: "positive", False: "negative"})
    )

    return annual_returns_df


def calculate_arr(annual_returns_df: pd.DataFrame) -> float:
    """Annualized Return Rate"""
    n_years = len(annual_returns_df)
    return (
        (1 + annual_returns_df["annual_return"].div(100)).prod() ** (1 / n_years) - 1
    ) * 100
