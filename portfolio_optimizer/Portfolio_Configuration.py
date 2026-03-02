import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_optimizer.market_data_service import get_ticker_details

if "tickers" not in st.session_state:
    st.session_state.tickers = "IUSQ.DE;EUNL.DE;IUSN.DE;EUNM.DE"
    st.session_state["allocation_IUSQ.DE"] = 50
    st.session_state["allocation_EUNL.DE"] = 30
    st.session_state["allocation_IUSN.DE"] = 10
    st.session_state["allocation_EUNM.DE"] = 10

portfolio_items = []
for i, item in enumerate(st.session_state.tickers.split(";")):
    try:
        ticker_data = get_ticker_details(item)
        portfolio_items.append({"ticker": item, **ticker_data})
    except Exception as e:
        st.error(e)
        st.stop()

portfolio_df = pd.DataFrame.from_dict(portfolio_items)

"# Portfolio Optimizer"

"## Portfolio Configuration"

st.text_input("Tickers present in your portfolio (separated by ';')", key="tickers")

columns = st.columns(2)

for item in portfolio_df.itertuples():
    col = columns[item.Index % 2]
    with col:
        st.number_input(
            f"Allocation of '{item.ticker}' (%)",
            min_value=0,
            max_value=100,
            key=f"allocation_{item.ticker}",
        )


portfolio_df["allocation"] = portfolio_df["ticker"].map(
    lambda ticker: st.session_state[f"allocation_{ticker}"]
)

if portfolio_df["allocation"].sum() != 100:
    st.error("Sum of allocation accross all assets must be 100")
    st.stop()

st.session_state.portfolio_df = portfolio_df

"## Portfolio"
"### Assets"
# portfolio pie chart
fig = px.pie(portfolio_df, values="allocation", names="name", hole=0.3)
fig.update_traces(textinfo="label+percent")
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

# portfolio df
st.dataframe(
    portfolio_df[["ticker", "name", "currency", "allocation"]], hide_index=True
)
