import streamlit as st

from utils import ensure_portfolio_configured

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Returns Analysis"
"## Growth Index"
