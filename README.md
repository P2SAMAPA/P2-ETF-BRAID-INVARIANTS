# Topological Braid / Knot Invariants Engine

Quantifies entanglement of ETF price paths using braid group crossing counts. For each rolling window (63, 126, 252 days), we track the order of paths day by day; each swap of two paths counts as a crossing. ETFs with fewer crossings are more ordered (less entangled) – a positive signal.

- **Output per universe:** top 3 ETFs with lowest crossing counts, plus the window that achieved that minimum.
- **Dashboard:** shows top ETFs, full ranking table, and total crossing complexity per window.
- Runs daily on GitHub Actions.

## Local execution

```bash
pip install -r requirements.txt
export HF_TOKEN=<your_token>
python trainer.py
streamlit run streamlit_app.py
