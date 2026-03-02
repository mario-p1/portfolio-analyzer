import pandas as pd

from config import EURIBOR_3M_PATH


def load_risk_free_rates():
    df = pd.read_csv(EURIBOR_3M_PATH, usecols=[0, 2], parse_dates=[0])
    df.columns = ["date", "annual_rate"]
    df = df.resample("ME", on="date").last()

    df["annual_rate"] = df["annual_rate"].div(100)

    # TODO: Use effective annual rates instead of average of the monthly rates
    df = (
        df.resample("YE")["annual_rate"]
        .mean()
        .to_frame()
        .rename(columns={"annual_rate": "risk_free_annual_rate"})
    )
    return df
