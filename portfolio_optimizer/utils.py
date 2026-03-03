import pandas as pd
import streamlit as st


def rename_ticker_columns_to_names(
    df: pd.DataFrame, ticker_df: pd.DataFrame
) -> pd.DataFrame:
    names_dict = ticker_df.set_index("ticker")["name"].to_dict()
    return df.rename(columns=names_dict)


def ensure_portfolio_configured():
    if "portfolio_df" not in st.session_state:
        st.error("Please go to the 'Configuration' page to configure your portfolio.")
        st.stop()


fig_layout = {
    "hovermode": "x unified",
    "legend": {
        "title": "",
        "orientation": "h",
        "yanchor": "top",
        "y": -0.2,
        "xanchor": "center",
        "x": 0.5,
    },
}
