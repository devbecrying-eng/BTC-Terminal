<p align="center">
  <img src="assets/banner.svg" alt="BTC Terminal" width="100%" />
</p>

<p align="center">
  <img src="assets/logo.svg" alt="BTC Terminal Logo" width="140" />
</p>

# BTC Terminal

A cyberpunk-style local dashboard to monitor BTC spot vs derivatives arbitrage (basis/spread %) with charts, setups, and optional AI-assisted analysis.

## Features
- Track **arbitrage spread / basis %** over time (spot vs derivatives)
- Dashboard indicators for **trend, momentum, and volume**
- Built to run **locally on Windows 11** (Python)

## Quickstart

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run btc_dashboard/btc_dashboard.py
```

## Repo hygiene
- Put secrets in `.env` (ignored) or `.streamlit/secrets.toml` (ignored).
- Use `.env.example` as a template.

## License
MIT — see `LICENSE`.
