import pandas as pd

from config import EURIBOR_3M_PATH


def load_risk_free_rates() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns:
    - monthly_df
    - annual_df
    """
    df = pd.read_csv(EURIBOR_3M_PATH, usecols=[0, 2], parse_dates=[0])
    df.columns = ["date", "rate"]

    monthly_df = df.resample("ME", on="date").last()
    monthly_df["rate"] = ((1 + monthly_df["rate"] / 100) ** (1 / 12) - 1) * 100

    annual_df = df.resample("YE", on="date").mean()
    return monthly_df, annual_df
