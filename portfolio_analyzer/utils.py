import pandas as pd
import streamlit as st


def rename_ticker_columns_to_names(
    df: pd.DataFrame, ticker_df: pd.DataFrame, name_col: str = "name"
) -> pd.DataFrame:
    names_dict = ticker_df.set_index("ticker")[name_col].to_dict()
    return df.rename(columns=names_dict)


def ensure_portfolio_configured():
    if "portfolio_df" not in st.session_state:
        st.error("Please go to the 'Configuration' page to configure your portfolio.")
        st.stop()


def load_value(key):
    if key in st.session_state:
        st.session_state[f"_{key}"] = st.session_state[key]


def store_value(key):
    st.session_state[key] = st.session_state[f"_{key}"]


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
