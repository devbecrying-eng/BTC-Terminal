# BTC Arbitrage Dashboard (Local)

A futuristic Streamlit dashboard that tracks **BTC** and multiple token derivatives (EVM/Solana/Sui, etc.) and highlights **relative-value / arbitrage-style divergences** in real time.

- Runs **locally on Windows 11**
- Uses **public endpoints only** (no API keys)
  - BTC spot: Binance public REST
  - Tokens: DexScreener public API (by contract address)

> ⚠️ Educational tool. Not financial advice. Crypto markets are risky. Leverage can liquidate you fast.

---

## Quick Start (Windows)

1) Install **Python 3.10+**
2) Open this folder
3) Double-click **START.bat**
4) Dashboard opens at: `http://localhost:8501`

---

## Manual Start

```bash
pip install -r requirements.txt
streamlit run btc_dashboard.py
```

---

## What it Shows

- **One main graph** that can display:
  - Normalized live prices (BTC + all tracked tokens)
  - Divergence vs BTC (% return spread)
- **Best arbitrage opportunity** widget (ranked by executable divergence)
- Per-asset **Long/Short setups** based on:
  - Trend (EMA regime + slope)
  - Momentum (RSI + MACD)
  - Volume (BTC volume vs moving average; token uses DexScreener volume when available)
- **Key prices to watch** (recent pivot levels)

---

## Customize Tokens

Edit `TOKENS` in `btc_dashboard.py` to add/remove tokens or change addresses.

---

## Files

- `btc_dashboard.py` — main app
- `requirements.txt` — deps
- `START.bat` — Windows launcher
