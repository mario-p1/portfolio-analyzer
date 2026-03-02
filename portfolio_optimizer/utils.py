import pandas as pd


def rename_ticker_columns_to_names(
    df: pd.DataFrame, ticker_df: pd.DataFrame
) -> pd.DataFrame:
    names_dict = ticker_df.set_index("ticker")["name"].to_dict()
    return df.rename(columns=names_dict)


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
