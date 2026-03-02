.PHONY:
dev:
	uv run python -m streamlit run portfolio_optimizer/Portfolio_Configuration.py --server.address 127.0.0.1 --server.runOnSave true