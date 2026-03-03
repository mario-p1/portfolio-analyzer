import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data
def get_ticker_details(ticker):
    data = yf.Ticker(ticker).get_info()

    if "longName" not in data.keys():
        raise ValueError(f"Ticker '{ticker}' doesn't exist.")

    return {"name": data["longName"], "currency": data["currency"]}


@st.cache_data
def get_price_history(ticker: str) -> pd.DataFrame:
    yticker = yf.Ticker(ticker)

    history_df = yticker.history(period="max", interval="1mo")
    return history_df


@st.cache_data
def get_prices_df(tickers: list[str]) -> pd.DataFrame:
    prices_df = pd.DataFrame()
    for ticker in tickers:
        history = (
            get_price_history(ticker)["Close"]
            .to_frame()
            .reset_index(drop=False)
            .rename(columns={"Date": "date", "Close": "close"})
        )

        history["date"] = history["date"].dt.tz_convert(None)
        history = history.resample("ME", on="date").last()

        prices_df = prices_df.merge(
            history["close"], left_index=True, right_index=True, how="outer"
        ).rename(columns={"close": ticker})

    return prices_df
