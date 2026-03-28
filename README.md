## Disclaimer

This project is a **experimental tool** created for learning and demonstration purposes.

**It is not intended for production use or real financial decision-making.**

The models and results provided may be simplified and are not guaranteed to be accurate.
Use at your own risk.

# Portfolio Optimization
Portfolio Optimizer is an interactive web application for analyzing, visualizing, and forecasting investment portfolio performance.
Built with Streamlit, it allows users to configure their own portfolios, fetch historical market data, and perform comprehensive return and risk analyses.

## Key features
- Portfolio Configuration: Define your portfolio by selecting assets and allocations.
- Returns Analysis: Visualize historical growth, annual and monthly returns, and compare performance against risk-free rates (Euribor 3M).
- Risk Analysis: Assess portfolio risk using metrics like maximum drawdown and Value at Risk (VaR).
- Forecasting: Run Monte Carlo simulations to forecast future portfolio values based on historical returns.
- Interactive Visualizations: Explore your portfolio with dynamic charts and tables powered by Plotly and Streamlit.

## Code Structure Overview

The application is organized as follows:

- `pyproject.toml`: Project configuration and dependencies.
- `Configuration.py`: Streamlit page for portfolio setup and asset allocation.
- `pages/`: Contains the main Streamlit analysis pages:
  - `1_Returns.py`: Analyzes and visualizes historical returns, growth, and Sharpe ratio.
  - `2_Risks.py`: Computes and visualizes risk metrics such as drawdown and Value at Risk.
  - `3_Forecast.py`: Runs Monte Carlo simulations for portfolio value forecasting.
- `market_data_service.py`: Service for fetching historical market data.
- `portfolio_metrics.py`: Functions for calculating portfolio growth, returns, risk metrics, and performance statistics.
- `interest_data_service.py`: Service for loading interest rate data (Euribor 3M).
- `utils.py`: Helper functions and Streamlit session management.

## TODOs
- [x] Add info to README.md
- [ ] Add explanation in streamlit
- [ ] Add monthly return heatmaps
- [ ] Add 2-3 more visualizations
