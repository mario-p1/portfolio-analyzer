import streamlit as st

from portfolio_optimizer.utils import ensure_portfolio_configured

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Returns Analysis"
"## Growth Index"
