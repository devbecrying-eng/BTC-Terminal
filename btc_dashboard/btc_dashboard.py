"""
BTC Multi-Exchange Terminal — NEMESIS UI
Dark industrial HUD aesthetic with animated background,
exchange-matched accent colors, glowing widgets, motion effects.
"""

import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests

st.set_page_config(page_title="BTC TERMINAL", page_icon="⬡", layout="wide", initial_sidebar_state="collapsed")

# ── Exchange brand colors ──────────────────────────────────────────────────────
EXCHANGE_COLORS = {
    "Binance":  {"primary": "#F0B90B", "glow": "rgba(240,185,11,0.25)",  "soft": "rgba(240,185,11,0.08)"},
    "Kraken":   {"primary": "#5741D9", "glow": "rgba(87,65,217,0.25)",   "soft": "rgba(87,65,217,0.08)"},
    "Coinbase": {"primary": "#0052FF", "glow": "rgba(0,82,255,0.25)",    "soft": "rgba(0,82,255,0.08)"},
    "Bybit":    {"primary": "#F7A600", "glow": "rgba(247,166,0,0.25)",   "soft": "rgba(247,166,0,0.08)"},
}

# ── CSS — full redesign ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@200;300;400;600;800&display=swap');

:root {
    --bg:       #06060a;
    --s1:       #0c0c12;
    --s2:       #10101a;
    --border:   #1a1a28;
    --border2:  #252535;
    --btc:      #f7931a;
    --btc-glow: rgba(247,147,26,0.3);
    --btc-soft: rgba(247,147,26,0.08);
    --green:    #00e5a0;
    --green-g:  rgba(0,229,160,0.25);
    --red:      #ff3355;
    --red-g:    rgba(255,51,85,0.25);
    --text:     #ddddf0;
    --sub:      #6b6b8a;
    --muted:    #3a3a52;
    --ex-color: #f7931a;
    --ex-glow:  rgba(247,147,26,0.25);
    --ex-soft:  rgba(247,147,26,0.08);
}

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body { height: 100%; }

[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Rajdhani', sans-serif;
    color: var(--text);
    position: relative;
    overflow-x: hidden;
}

/* Animated mesh background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(247,147,26,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 80% 90%, rgba(247,147,26,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(30,30,60,0.8) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: meshShift 18s ease-in-out infinite alternate;
}

@keyframes meshShift {
    0%   { background-position: 0% 0%; opacity: 1; }
    50%  { background-position: 100% 100%; opacity: 0.8; }
    100% { background-position: 0% 100%; opacity: 1; }
}

/* Scanlines overlay */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.08) 2px,
        rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    padding: 1.2rem 1.6rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border2), transparent) !important;
    margin: 0.8rem 0 !important;
}

/* ── HUD Header ── */
.hud-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 1.2rem;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, rgba(12,12,18,0.95), rgba(16,16,26,0.95));
    border: 1px solid var(--border2);
    border-top: 2px solid var(--btc);
    border-radius: 4px 4px 8px 8px;
    box-shadow: 0 0 40px var(--btc-glow), inset 0 1px 0 rgba(247,147,26,0.1);
    position: relative;
    overflow: hidden;
}
.hud-header::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--btc), transparent);
    animation: scanLine 4s linear infinite;
}
@keyframes scanLine {
    0%   { left: -60%; }
    100% { left: 160%; }
}
.hud-logo {
    font-family: 'Exo 2', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--btc);
    text-shadow: 0 0 20px var(--btc-glow), 0 0 40px rgba(247,147,26,0.2);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.hud-logo-hex {
    font-size: 1.2rem;
    animation: hexPulse 2s ease-in-out infinite;
}
@keyframes hexPulse {
    0%, 100% { opacity: 1; text-shadow: 0 0 10px var(--btc); }
    50%       { opacity: 0.5; text-shadow: none; }
}
.hud-meta {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: var(--sub);
    letter-spacing: 0.1em;
    text-align: right;
    line-height: 1.6;
}
.hud-ex-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    border: 1px solid var(--ex-color);
    color: var(--ex-color);
    background: var(--ex-soft);
    box-shadow: 0 0 12px var(--ex-glow);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    animation: badgePulse 3s ease-in-out infinite;
}
@keyframes badgePulse {
    0%, 100% { box-shadow: 0 0 8px var(--ex-glow); }
    50%       { box-shadow: 0 0 20px var(--ex-glow), 0 0 40px var(--ex-soft); }
}

/* ── Section label ── */
.sec {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--sub);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.55rem;
}
.sec::before {
    content: '';
    display: inline-block;
    width: 14px; height: 2px;
    background: var(--btc);
    box-shadow: 0 0 6px var(--btc-glow);
}
.sec::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border2), transparent);
}

/* ── Price Cards ── */
.pcard {
    background: linear-gradient(135deg, var(--s1), var(--s2));
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    cursor: default;
}
.pcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--ex-color), transparent);
    opacity: 0.6;
}
.pcard:hover {
    border-color: var(--ex-color);
    box-shadow: 0 0 24px var(--ex-glow), 0 8px 32px rgba(0,0,0,0.4);
    transform: translateY(-3px);
}
.pcard:hover::before { opacity: 1; }

.pcard-corner {
    position: absolute;
    top: 6px; right: 8px;
    width: 8px; height: 8px;
    border-top: 1px solid var(--ex-color);
    border-right: 1px solid var(--ex-color);
    opacity: 0.5;
}
.pcard-corner-bl {
    position: absolute;
    bottom: 6px; left: 8px;
    width: 8px; height: 8px;
    border-bottom: 1px solid var(--muted);
    border-left: 1px solid var(--muted);
    opacity: 0.3;
}
.pcard-exname {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ex-color);
    margin-bottom: 0.15rem;
    text-shadow: 0 0 8px var(--ex-glow);
}
.pcard-price {
    font-family: 'Exo 2', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.02em;
    line-height: 1.1;
}
.pcard-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.63rem;
    color: var(--sub);
    margin-top: 0.25rem;
    letter-spacing: 0.04em;
}
.pcard-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    margin-right: 0.3rem;
    animation: blink 1.5s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.2; }
}
.dot-green { background: var(--green); box-shadow: 0 0 6px var(--green-g); }
.dot-red   { background: var(--red);   box-shadow: 0 0 6px var(--red-g); }

/* ── Glowing number ── */
.glow-green { color: var(--green); text-shadow: 0 0 12px var(--green-g); }
.glow-red   { color: var(--red);   text-shadow: 0 0 12px var(--red-g); }
.glow-btc   { color: var(--btc);   text-shadow: 0 0 12px var(--btc-glow); }

/* ── Widget card (signals, levels etc) ── */
.wcard {
    background: linear-gradient(135deg, rgba(12,12,18,0.9), rgba(10,10,16,0.95));
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 0.85rem 0.95rem;
    position: relative;
    overflow: hidden;
}
.wcard::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--muted), transparent);
}

/* ── Signal rows ── */
.sig-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.35rem 0.55rem;
    border-radius: 4px;
    margin-bottom: 0.18rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    background: rgba(255,255,255,0.02);
    border-left: 2px solid transparent;
    transition: all 0.2s;
}
.sig-row:hover { background: rgba(255,255,255,0.04); transform: translateX(3px); }
.sig-bull { border-color: var(--green); }
.sig-bear { border-color: var(--red); }
.sig-neu  { border-color: var(--btc); }
.sig-name { color: var(--sub); }
.sv-bull  { color: var(--green); font-weight: 700; text-shadow: 0 0 8px var(--green-g); }
.sv-bear  { color: var(--red);   font-weight: 700; text-shadow: 0 0 8px var(--red-g); }
.sv-neu   { color: var(--btc);   font-weight: 700; }

/* ── Level rows ── */
.level-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0.6rem;
    border-radius: 4px;
    margin-bottom: 0.22rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    background: rgba(255,255,255,0.02);
    border-left: 2px solid;
    transition: all 0.2s;
}
.level-row:hover { background: rgba(255,255,255,0.04); transform: translateX(3px); }
.level-sup { border-color: var(--green); }
.level-res { border-color: var(--red); }
.level-name { color: var(--sub); font-size: 0.6rem; }
.lp-sup { color: var(--green); font-weight: 700; text-shadow: 0 0 6px var(--green-g); }
.lp-res { color: var(--red);   font-weight: 700; text-shadow: 0 0 6px var(--red-g); }

/* ── Alert rows ── */
.alert-row {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.38rem 0.6rem;
    border-radius: 4px;
    margin-bottom: 0.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    line-height: 1.5;
    transition: all 0.2s;
}
.alert-row:hover { transform: translateX(3px); }
.a-danger { background: rgba(255,51,85,0.08);  border-left: 2px solid var(--red);   color: var(--red); }
.a-warn   { background: rgba(247,147,26,0.08); border-left: 2px solid var(--btc);   color: var(--btc); }
.a-ok     { background: rgba(0,229,160,0.06);  border-left: 2px solid var(--green); color: var(--green); }
.alert-icon { font-size: 0.7rem; flex-shrink: 0; margin-top: 0.05rem; }
.alert-body strong { display: block; font-size: 0.63rem; letter-spacing: 0.08em; margin-bottom: 0.1rem; }

/* ── Trade setup boxes ── */
.setup-box {
    border-radius: 6px;
    padding: 0.8rem 0.95rem;
    margin-bottom: 0.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.66rem;
    position: relative;
    overflow: hidden;
}
.setup-long  {
    background: linear-gradient(135deg, rgba(0,229,160,0.05), rgba(0,229,160,0.02));
    border: 1px solid rgba(0,229,160,0.2);
    border-left: 3px solid var(--green);
}
.setup-short {
    background: linear-gradient(135deg, rgba(255,51,85,0.05), rgba(255,51,85,0.02));
    border: 1px solid rgba(255,51,85,0.2);
    border-left: 3px solid var(--red);
}
.setup-hdr   { display: flex; justify-content: space-between; margin-bottom: 0.55rem; align-items: center; }
.setup-long  .setup-tag { color: var(--green); font-weight: 700; font-size: 0.75rem; letter-spacing: 0.1em; text-shadow: 0 0 10px var(--green-g); }
.setup-short .setup-tag { color: var(--red);   font-weight: 700; font-size: 0.75rem; letter-spacing: 0.1em; text-shadow: 0 0 10px var(--red-g); }
.setup-note { color: var(--muted); font-size: 0.58rem; }
.setup-grid { display: grid; grid-template-columns: auto 1fr; gap: 0.18rem 0.9rem; }
.sg-l { color: var(--sub); white-space: nowrap; }
.sg-v { color: var(--text); font-weight: 600; }
.sg-tp  { color: var(--green); text-shadow: 0 0 6px var(--green-g); }
.sg-rr  { color: var(--btc); text-shadow: 0 0 6px var(--btc-glow); }
.sg-inv { color: var(--red); font-size: 0.62rem; }

/* ── Scenario cards ── */
.scenario {
    border-radius: 5px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.4rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    line-height: 1.6;
    border-left: 3px solid;
    transition: all 0.2s;
}
.scenario:hover { transform: translateX(4px); }
.sc-bull { background: rgba(0,229,160,0.04); border-color: var(--green); }
.sc-bear { background: rgba(255,51,85,0.04); border-color: var(--red); }
.sc-title { font-size: 0.7rem; font-weight: 700; margin-bottom: 0.3rem; letter-spacing: 0.06em; }
.sc-bull .sc-title { color: var(--green); text-shadow: 0 0 8px var(--green-g); }
.sc-bear .sc-title { color: var(--red);   text-shadow: 0 0 8px var(--red-g); }
.sc-text { color: var(--sub); }

/* ── RSI card ── */
.rsi-card {
    background: linear-gradient(135deg, var(--s1), var(--s2));
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.rsi-num {
    font-family: 'Exo 2', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.02em;
}
.rsi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    margin-top: 0.2rem;
}
.rsi-bar-bg {
    width: 100%; height: 4px;
    background: var(--border);
    border-radius: 2px;
    margin-top: 0.5rem;
    overflow: hidden;
}
.rsi-bar { height: 100%; border-radius: 2px; transition: width 0.6s; }

/* ── Fear & Greed ── */
.fg-card {
    background: linear-gradient(135deg, var(--s1), var(--s2));
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    text-align: center;
}
.fg-ring-wrap { position: relative; width: 90px; height: 90px; margin: 0 auto 0.4rem; }
.fg-num {
    font-family: 'Exo 2', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
}
.fg-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    color: var(--sub);
    text-transform: uppercase;
}

/* ── Buttons — HUD style ── */
.stButton > button {
    background: linear-gradient(135deg, var(--s1), var(--s2)) !important;
    border: 1px solid var(--border2) !important;
    color: var(--sub) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.68rem !important;
    border-radius: 4px !important;
    padding: 0.4rem 1rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::before {
    content: '' !important;
    position: absolute !important;
    top: 0; left: -100%; width: 100%; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(247,147,26,0.1), transparent) !important;
    transition: left 0.4s !important;
}
.stButton > button:hover {
    border-color: var(--btc) !important;
    color: var(--btc) !important;
    box-shadow: 0 0 16px var(--btc-glow), 0 4px 20px rgba(0,0,0,0.4) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:hover::before { left: 100% !important; }
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    background: var(--s1) !important;
    border-color: var(--border2) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    color: var(--sub) !important;
    border-radius: 4px !important;
}
div[data-baseweb="select"] > div:hover { border-color: var(--btc) !important; }

/* ── Dataframe ── */
.stDataFrame { border: 1px solid var(--border2) !important; border-radius: 6px; }
[data-testid="stDataFrameResizable"] th {
    background: var(--s1) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.08em !important;
    color: var(--sub) !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrameResizable"] td {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.68rem !important;
}

/* ── SFP badges ── */
.sfp-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0.55rem;
    border-radius: 4px;
    margin-bottom: 0.18rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    background: rgba(255,255,255,0.02);
    transition: all 0.2s;
}
.sfp-row:hover { transform: translateX(3px); background: rgba(255,255,255,0.04); }
.sfp-bull { color: var(--green); text-shadow: 0 0 6px var(--green-g); }
.sfp-bear { color: var(--red);   text-shadow: 0 0 6px var(--red-g); }
.sfp-price { color: var(--sub); }

/* ── Spinner override ── */
.stSpinner > div { border-top-color: var(--btc) !important; }

/* ── Animated corner decorations ── */
@keyframes cornerGlow {
    0%,100% { opacity: 0.3; }
    50%      { opacity: 0.9; }
}

/* ── Status dot ── */
.live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green-g);
    animation: blink 1.5s ease-in-out infinite;
    margin-right: 0.3rem;
}

/* ── Ticker strip ── */
.ticker-wrap {
    overflow: hidden;
    white-space: nowrap;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: var(--sub);
    letter-spacing: 0.08em;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 0.2rem 0;
    margin-bottom: 0.8rem;
    background: rgba(0,0,0,0.3);
}
.ticker-inner {
    display: inline-block;
    animation: tickerScroll 30s linear infinite;
}
@keyframes tickerScroll {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* ── Grid lines ── */
.grid-line {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--border2) 20%, var(--border2) 80%, transparent 100%);
    margin: 0.75rem 0;
}

/* ── Active exchange selector ── */
.ex-pill {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid;
    margin-left: 0.3rem;
    cursor: default;
}
</style>
""", unsafe_allow_html=True)

# ── Exchange setup ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_exchanges():
    return {
        "Binance":  ccxt.binance({"enableRateLimit": True}),
        "Kraken":   ccxt.kraken({"enableRateLimit": True}),
        "Coinbase": ccxt.coinbase({"enableRateLimit": True}),
        "Bybit":    ccxt.bybit({"enableRateLimit": True}),
    }

exchanges = get_exchanges()
SYMBOLS = {"Binance": "BTC/USDT", "Kraken": "BTC/USD", "Coinbase": "BTC/USD", "Bybit": "BTC/USDT"}

def pfmt(val, d=2):
    if val is None: return "—"
    try: return f"${val:,.{d}f}"
    except: return "—"

def pct_fmt(val):
    if val is None: return "0.00%"
    try:
        s = "+" if val >= 0 else ""
        return f"{s}{val:.2f}%"
    except: return "—"

# ── Data fetchers ─────────────────────────────────────────────────────────────
def fetch_tickers():
    out = {}
    for name, ex in exchanges.items():
        try:
            t = ex.fetch_ticker(SYMBOLS[name])
            out[name] = {k: t.get(k) for k in ("last","bid","ask","quoteVolume","baseVolume","percentage","high","low")}
            out[name]["price"]  = out[name]["last"]
            out[name]["volume"] = out[name]["quoteVolume"] or out[name]["baseVolume"]
            out[name]["change"] = out[name]["percentage"]
        except:
            out[name] = None
    return out

def fetch_ohlcv(exname="Binance", tf="1h", limit=200):
    try:
        ex   = exchanges[exname]
        data = ex.fetch_ohlcv(SYMBOLS[exname], tf, limit=limit)
        df   = pd.DataFrame(data, columns=["ts","open","high","low","close","volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        return df.set_index("ts")
    except:
        return None

def fetch_orderbook(exname="Binance", limit=25):
    try: return exchanges[exname].fetch_order_book(SYMBOLS[exname], limit=limit)
    except: return None

def fetch_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        d = r.json()["data"][0]
        return int(d["value"]), d["value_classification"]
    except:
        return None, None

# ── Indicators ─────────────────────────────────────────────────────────────────
def calc_rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0).rolling(p).mean()
    l = -d.clip(upper=0).rolling(p).mean()
    return 100 - (100 / (1 + g / (l + 1e-10)))

def calc_macd(s, fast=12, slow=26, sig=9):
    ef = s.ewm(span=fast).mean()
    es = s.ewm(span=slow).mean()
    m  = ef - es
    sg = m.ewm(span=sig).mean()
    return m, sg, m - sg

def calc_bb(s, p=20, std=2):
    mid = s.rolling(p).mean()
    sd  = s.rolling(p).std()
    return mid + std*sd, mid, mid - std*sd

def calc_ema(s, p): return s.ewm(span=p).mean()

def detect_sfp(df, lookback=20):
    sfps = []
    if df is None: return sfps
    H, L, C = df["high"].values, df["low"].values, df["close"].values
    for i in range(lookback, len(df)):
        rh, rl = H[i-lookback:i].max(), L[i-lookback:i].min()
        if H[i] > rh and C[i] < rh:
            sfps.append({"ts": df.index[i], "type": "bearish", "price": H[i]})
        elif L[i] < rl and C[i] > rl:
            sfps.append({"ts": df.index[i], "type": "bullish", "price": L[i]})
    return sfps

def calc_key_levels(df):
    if df is None or len(df) < 50: return [], []
    highs = df["high"].rolling(5, center=True).max()
    lows  = df["low"].rolling(5, center=True).min()
    sh = df["high"][(df["high"] == highs) & (df["high"] == df["high"].rolling(20, center=True).max())]
    sl = df["low"][(df["low"] == lows)   & (df["low"]  == df["low"].rolling(20, center=True).min())]
    return sorted(sl.nsmallest(3).tolist()), sorted(sh.nlargest(3).tolist(), reverse=True)

def build_signals(df):
    sigs = []
    if df is None or len(df) < 50: return sigs
    close  = df["close"]
    rsi_v  = calc_rsi(close).iloc[-1]
    macd_l, sig_l, hist = calc_macd(close)
    ema20  = calc_ema(close, 20).iloc[-1]
    ema50  = calc_ema(close, 50).iloc[-1]
    ema200 = calc_ema(close, 200).iloc[-1] if len(df) >= 200 else None
    bb_u, bb_m, bb_l = calc_bb(close)
    last   = close.iloc[-1]
    vol_avg = df["volume"].rolling(20).mean().iloc[-1]
    vol_now = df["volume"].iloc[-1]
    macd_now, hist_now = macd_l.iloc[-1], hist.iloc[-1]
    vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1

    # RSI
    lbl = "OVERBOUGHT" if rsi_v > 70 else "OVERSOLD" if rsi_v < 30 else "NEUTRAL"
    bias = "bear" if rsi_v > 70 else "bull" if rsi_v < 30 else "neu"
    sigs.append(("RSI", f"{rsi_v:.1f}", lbl, bias))

    # MACD
    if macd_now > 0 and hist_now > 0:  sigs.append(("MACD", f"{macd_now:.0f}", "BULLISH", "bull"))
    elif macd_now < 0 and hist_now < 0: sigs.append(("MACD", f"{macd_now:.0f}", "BEARISH", "bear"))
    else:                               sigs.append(("MACD", f"{macd_now:.0f}", "CROSSING", "neu"))

    # EMA
    if last > ema20 > ema50: sigs.append(("EMA 20/50", pfmt(ema20,0), "BULL STACK", "bull"))
    elif last < ema20 < ema50: sigs.append(("EMA 20/50", pfmt(ema20,0), "BEAR STACK", "bear"))
    else:                     sigs.append(("EMA 20/50", pfmt(ema20,0), "MIXED", "neu"))

    if ema200:
        sigs.append(("EMA 200", pfmt(ema200,0), "ABOVE" if last > ema200 else "BELOW",
                     "bull" if last > ema200 else "bear"))

    # BB
    if last > bb_u.iloc[-1]:   sigs.append(("BOLL BANDS", pfmt(bb_u.iloc[-1],0), "ABOVE UPPER", "bear"))
    elif last < bb_l.iloc[-1]: sigs.append(("BOLL BANDS", pfmt(bb_l.iloc[-1],0), "BELOW LOWER", "bull"))
    else:
        pctb = (last - bb_l.iloc[-1]) / (bb_u.iloc[-1] - bb_l.iloc[-1]) * 100
        sigs.append(("BOLL BANDS", f"{pctb:.0f}%B", "MID RANGE", "neu"))

    # Volume
    v_bias = "bull" if df["close"].iloc[-1] > df["open"].iloc[-1] else "bear"
    if vol_ratio > 1.5:   sigs.append(("VOLUME", f"{vol_ratio:.1f}x avg", "HIGH VOL", v_bias))
    elif vol_ratio < 0.6: sigs.append(("VOLUME", f"{vol_ratio:.1f}x avg", "LOW VOL", "neu"))
    else:                  sigs.append(("VOLUME", f"{vol_ratio:.1f}x avg", "NORMAL", "neu"))

    return sigs

def detect_manipulation(tickers, df_1m=None):
    alerts = []
    prices = {k: v["price"] for k, v in tickers.items() if v and v.get("price") is not None}
    if len(prices) >= 2:
        mx, mn = max(prices.values()), min(prices.values())
        sp = (mx - mn) / mn * 100
        if sp > 0.5:   alerts.append(("SPREAD ANOMALY", f"{sp:.3f}% cross-exchange spread", "a-danger"))
        elif sp > 0.15: alerts.append(("SPREAD WATCH",  f"{sp:.3f}% cross-exchange spread", "a-warn"))
    for name, t in tickers.items():
        if t and t.get("bid") and t.get("ask"):
            ba = (t["ask"] - t["bid"]) / t["bid"] * 100
            if ba > 0.1: alerts.append((f"{name.upper()} WIDE B/A", f"Bid-ask {ba:.4f}%", "a-warn"))
    if df_1m is not None and len(df_1m) > 1:
        last = df_1m.iloc[-1]
        total = last["high"] - last["low"]
        if total > 0:
            wicks = (last["high"] - max(last["open"], last["close"])) + (min(last["open"], last["close"]) - last["low"])
            if wicks / total > 0.75:
                alerts.append(("WICK DOMINANCE", f"{wicks/total*100:.0f}% wick — stop hunt possible", "a-danger"))
    if not alerts:
        alerts.append(("CLEAN", "No manipulation signals", "a-ok"))
    return alerts

def build_trade_setups(df, tickers):
    if df is None or len(df) < 20: return None, None
    prices = [v["price"] for v in tickers.values() if v and v.get("price")]
    price  = sum(prices) / len(prices) if prices else df["close"].iloc[-1]
    atr    = (df["high"] - df["low"]).rolling(14).mean().iloc[-1]

    def mk(side):
        if side == "long":
            e = price - atr * 0.3
            sl = price - atr * 1.5
            t1 = price + atr * 1.0
            t2 = price + atr * 2.2
            t3 = price + atr * 3.5
        else:
            e = price + atr * 0.3
            sl = price + atr * 1.5
            t1 = price - atr * 1.0
            t2 = price - atr * 2.2
            t3 = price - atr * 3.5
        rr = round(abs(t2 - e) / abs(e - sl), 1) if abs(e - sl) > 0 else 0
        inv = pfmt(sl - atr*0.2, 0) if side == "long" else pfmt(sl + atr*0.2, 0)
        return {
            "entry": f"{pfmt(e-atr*.12,0)} — {pfmt(e+atr*.12,0)}",
            "sl": pfmt(sl, 0), "tp1": pfmt(t1, 0), "tp2": pfmt(t2, 0), "tp3": pfmt(t3, 0),
            "rr": f"1:{rr}", "invalid": inv,
        }
    return mk("long"), mk("short")


# ── Chart builders ─────────────────────────────────────────────────────────────
def ex_colors(exname):
    c = EXCHANGE_COLORS.get(exname, {"primary":"#f7931a","glow":"rgba(247,147,26,0.25)","soft":"rgba(247,147,26,0.08)"})
    return c["primary"], c["glow"]

BASE = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#06060a",
            font=dict(family="Share Tech Mono", color="#6b6b8a", size=10),
            margin=dict(l=8, r=8, t=28, b=8))
GRID = dict(gridcolor="#0f0f18", showgrid=True, zeroline=False)

def chart_price(df, sfps, exname, tf):
    ep, eg = ex_colors(exname)
    fig = make_subplots(rows=3, cols=1, row_heights=[0.6, 0.2, 0.2],
                        shared_xaxes=True, vertical_spacing=0.012)
    # Candles
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing=dict(fillcolor="#00e5a0", line=dict(color="#00e5a0", width=1)),
        decreasing=dict(fillcolor="#ff3355", line=dict(color="#ff3355", width=1)),
        showlegend=False), row=1, col=1)
    # EMAs
    fig.add_trace(go.Scatter(x=df.index, y=calc_ema(df["close"],20),
        line=dict(color=ep, width=1.2, dash="solid"), name="EMA20", showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=calc_ema(df["close"],50),
        line=dict(color="#5a5a7a", width=1, dash="dot"), name="EMA50", showlegend=True), row=1, col=1)
    # BB
    bb_u, bb_m, bb_l = calc_bb(df["close"])
    fig.add_trace(go.Scatter(x=df.index, y=bb_u, line=dict(color="#2a2a40", width=1),
        showlegend=False, fill=None), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb_l, line=dict(color="#2a2a40", width=1),
        fill="tonexty", fillcolor="rgba(42,42,64,0.08)", showlegend=False), row=1, col=1)
    # SFPs
    bs = [s for s in sfps if s["type"]=="bullish"]
    br = [s for s in sfps if s["type"]=="bearish"]
    if bs: fig.add_trace(go.Scatter(x=[s["ts"] for s in bs], y=[s["price"] for s in bs],
        mode="markers", marker=dict(symbol="triangle-up", color="#00e5a0", size=10,
            line=dict(color="#00e5a0", width=1)), name="SFP Bull", showlegend=False), row=1, col=1)
    if br: fig.add_trace(go.Scatter(x=[s["ts"] for s in br], y=[s["price"] for s in br],
        mode="markers", marker=dict(symbol="triangle-down", color="#ff3355", size=10,
            line=dict(color="#ff3355", width=1)), name="SFP Bear", showlegend=False), row=1, col=1)
    # Volume
    vc = ["#00e5a0" if c >= o else "#ff3355" for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], marker_color=vc, opacity=0.6,
        showlegend=False), row=2, col=1)
    # RSI
    rsi = calc_rsi(df["close"])
    fig.add_trace(go.Scatter(x=df.index, y=rsi,
        line=dict(color=ep, width=1.5), showlegend=False), row=3, col=1)
    fig.add_hline(y=70, line=dict(color="#ff3355", width=0.7, dash="dot"), row=3, col=1)
    fig.add_hline(y=30, line=dict(color="#00e5a0", width=0.7, dash="dot"), row=3, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(247,147,26,0.02)",
        line_width=0, row=3, col=1)

    fig.update_layout(**BASE,
        title=dict(text=f"{exname}  //  BTC  //  {tf}", font=dict(color=ep, size=10), x=0.01),
        height=500, xaxis_rangeslider_visible=False,
        xaxis=GRID, xaxis2=GRID, xaxis3=GRID,
        yaxis=dict(**GRID, side="right"),
        yaxis2=dict(**GRID, side="right"),
        yaxis3=dict(**GRID, side="right", range=[0,100]),
        legend=dict(orientation="h", x=0, y=1.04, font=dict(size=9,color="#6b6b8a"),
                    bgcolor="rgba(0,0,0,0)"),
    )
    return fig

def chart_arb(tickers):
    prices = {k: v["price"] for k, v in tickers.items() if v and v.get("price")}
    if len(prices) < 2: return None
    ref   = min(prices.values())
    names = list(prices.keys())
    diffs = [(prices[n]-ref)/ref*100 for n in names]
    mx    = max(diffs)
    bar_colors = []
    for n, d in zip(names, diffs):
        c = EXCHANGE_COLORS.get(n, {"primary":"#f7931a"})["primary"]
        bar_colors.append(c if d == mx else "#1a1a28")
    fig = go.Figure(go.Bar(x=names, y=diffs, marker_color=bar_colors,
        text=[f"+{d:.4f}%" if d>=0 else f"{d:.4f}%" for d in diffs],
        textposition="outside", textfont=dict(family="Share Tech Mono", size=10, color="#ddddf0")))
    fig.update_layout(**BASE,
        title=dict(text="Price Premium vs Cheapest (%)", font=dict(color="#6b6b8a",size=10), x=0.01),
        height=210, showlegend=False,
        xaxis=GRID,
        yaxis=dict(gridcolor="#0f0f18", showgrid=True, zeroline=True,
                   zerolinecolor="#2a2a40", ticksuffix="%", side="right"))
    return fig

def chart_orderbook(ob, exname):
    if not ob: return None
    ep, eg = ex_colors(exname)
    bids = pd.DataFrame(ob["bids"][:25], columns=["price","size"])
    asks = pd.DataFrame(ob["asks"][:25], columns=["price","size"])
    bids["cum"] = bids["size"].cumsum()
    asks["cum"] = asks["size"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bids["price"], y=bids["cum"],
        fill="tozeroy", fillcolor="rgba(0,229,160,0.07)",
        line=dict(color="#00e5a0", width=1.5), name="Bids"))
    fig.add_trace(go.Scatter(x=asks["price"], y=asks["cum"],
        fill="tozeroy", fillcolor="rgba(255,51,85,0.07)",
        line=dict(color="#ff3355", width=1.5), name="Asks"))
    fig.update_layout(**BASE,
        title=dict(text=f"Order Book Depth // {exname}", font=dict(color="#6b6b8a",size=10), x=0.01),
        height=210, xaxis=GRID, yaxis=dict(**GRID, side="right"),
        legend=dict(orientation="h", x=0, y=1.06, font=dict(size=9,color="#6b6b8a"),
                    bgcolor="rgba(0,0,0,0)"))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════════════════════════════════════

# ── Controls (must come before CSS injection of ex-color vars) ────────────────
c1, c2, c3, c4 = st.columns([1, 1, 1, 4])
with c1:
    timeframe = st.selectbox("tf", ["1m","5m","15m","1h","4h","1d"], index=3, label_visibility="collapsed")
with c2:
    chart_ex  = st.selectbox("ex", list(exchanges.keys()), label_visibility="collapsed")
with c3:
    do_refresh = st.button("⟳  Refresh")
with c4:
    st.markdown(
        f"<div style='font-family:Share Tech Mono;font-size:0.6rem;color:#3a3a52;padding-top:0.6rem;'>"
        f"SYS: ONLINE &nbsp;|&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
        unsafe_allow_html=True)

# Inject exchange color CSS variables dynamically
ec = EXCHANGE_COLORS.get(chart_ex, EXCHANGE_COLORS["Binance"])
st.markdown(f"""
<style>
:root {{
    --ex-color: {ec['primary']};
    --ex-glow:  {ec['glow']};
    --ex-soft:  {ec['soft']};
}}
</style>
""", unsafe_allow_html=True)

# ── HUD Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hud-header">
  <div class="hud-logo">
    <span class="hud-logo-hex">⬡</span>
    BTC&nbsp;TERMINAL
  </div>
  <div style="display:flex;align-items:center;gap:0.8rem;">
    <span style="font-family:Share Tech Mono;font-size:0.6rem;color:#3a3a52;letter-spacing:0.08em;">
      BINANCE &nbsp;·&nbsp; KRAKEN &nbsp;·&nbsp; COINBASE &nbsp;·&nbsp; BYBIT
    </span>
    <span class="hud-ex-badge">{chart_ex}</span>
    <span style="font-family:Share Tech Mono;font-size:0.6rem;color:#3a3a52;">
      <span class="live-dot"></span>LIVE
    </span>
  </div>
  <div class="hud-meta">
    {datetime.now().strftime('%d %b %Y')}<br>
    {SYMBOLS.get(chart_ex, 'BTC/USD')} &nbsp;·&nbsp; {timeframe}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Fetch data ─────────────────────────────────────────────────────────────────
with st.spinner(""):
    tickers      = fetch_tickers()
    df           = fetch_ohlcv(chart_ex, timeframe, limit=200)
    df_1m        = fetch_ohlcv(chart_ex, "1m", limit=10)
    ob           = fetch_orderbook(chart_ex)
    fg_val, fg_label = fetch_fear_greed()

sfps        = detect_sfp(df) if df is not None else []
signals     = build_signals(df)
sup_lvls, res_lvls = calc_key_levels(df)
long_s, short_s    = build_trade_setups(df, tickers)
manip_alerts       = detect_manipulation(tickers, df_1m)

# ── Ticker strip ──────────────────────────────────────────────────────────────
ticker_items = []
for n, t in tickers.items():
    if t and t.get("price"):
        chg = t["change"] or 0.0
        sign = "+" if chg >= 0 else ""
        col = "#00e5a0" if chg >= 0 else "#ff3355"
        ticker_items.append(
            f'<span style="color:#3a3a52;">{n}</span> '
            f'<span style="color:#ddddf0;">{pfmt(t["price"])}</span> '
            f'<span style="color:{col};">{sign}{chg:.2f}%</span>'
            f'<span style="color:#1a1a28;"> &nbsp;&nbsp;|&nbsp;&nbsp; </span>'
        )
strip = "".join(ticker_items * 4)
st.markdown(f'<div class="ticker-wrap"><div class="ticker-inner">{strip}</div></div>',
            unsafe_allow_html=True)

# ── ROW 1: Price cards ────────────────────────────────────────────────────────
st.markdown('<div class="sec">Live Prices</div>', unsafe_allow_html=True)
p_cols = st.columns(4)
for i, name in enumerate(list(exchanges.keys())):
    t  = tickers.get(name)
    ec_local = EXCHANGE_COLORS.get(name, {"primary":"#f7931a","glow":"rgba(247,147,26,0.25)","soft":"rgba(247,147,26,0.08)"})
    ep_local = ec_local["primary"]
    eg_local = ec_local["glow"]
    es_local = ec_local["soft"]
    with p_cols[i]:
        if t and t.get("price") is not None:
            chg  = t["change"] if t["change"] is not None else 0.0
            cc   = "glow-green" if chg >= 0 else "glow-red"
            dc   = "dot-green"  if chg >= 0 else "dot-red"
            chg_sign = "+" if chg >= 0 else ""
            is_active = " style='border-color:" + ep_local + ";box-shadow:0 0 24px " + eg_local + ";'" if name == chart_ex else ""
            st.markdown(f"""
<div class="pcard"{is_active}>
  <div class="pcard-corner"></div>
  <div class="pcard-corner-bl"></div>
  <div class="pcard-exname" style="color:{ep_local};text-shadow:0 0 8px {eg_local};">{name}</div>
  <div class="pcard-price">{pfmt(t['price'])}</div>
  <div class="pcard-sub">
    <span class="{cc}">{chg_sign}{chg:.2f}%</span>
    &nbsp;&middot;&nbsp;
    H:{pfmt(t.get('high'),0)}&nbsp;L:{pfmt(t.get('low'),0)}
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="pcard">
  <div class="pcard-exname" style="color:{ep_local};">{name}</div>
  <div class="pcard-price" style="color:#3a3a52;">—</div>
  <div class="pcard-sub">Unavailable</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)

# ── ROW 2: Chart + Signal panel ───────────────────────────────────────────────
ch_col, sig_col = st.columns([3, 1])

with ch_col:
    st.markdown(f'<div class="sec">Candlestick &nbsp;·&nbsp; EMA &nbsp;·&nbsp; BB &nbsp;·&nbsp; Volume &nbsp;·&nbsp; RSI</div>', unsafe_allow_html=True)
    if df is not None:
        st.plotly_chart(chart_price(df, sfps, chart_ex, timeframe),
                        use_container_width=True, config={"displayModeBar": False})
    else:
        st.error("OHLCV unavailable")

with sig_col:
    # Signals
    st.markdown('<div class="sec">Technical Signals</div>', unsafe_allow_html=True)
    for name, val, label, bias in signals:
        rc = "sig-bull" if bias=="bull" else "sig-bear" if bias=="bear" else "sig-neu"
        vc = "sv-bull"  if bias=="bull" else "sv-bear"  if bias=="bear" else "sv-neu"
        st.markdown(f"""
<div class="sig-row {rc}">
  <span class="sig-name">{name}</span>
  <span class="{vc}">{label}</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)

    # RSI widget
    if df is not None:
        rv = calc_rsi(df["close"]).iloc[-1]
        if rv > 70:   rc, rl, rbar = "#ff3355", "OVERBOUGHT", "background:#ff3355;"
        elif rv < 30: rc, rl, rbar = "#00e5a0", "OVERSOLD",   "background:#00e5a0;"
        else:         rc, rl, rbar = "#f7931a", "NEUTRAL",    "background:#f7931a;"
        st.markdown(f"""
<div class="rsi-card">
  <div class="rsi-num" style="color:{rc};text-shadow:0 0 20px {rc}44;">{rv:.1f}</div>
  <div class="rsi-label" style="color:{rc};letter-spacing:0.15em;">{rl}</div>
  <div class="rsi-bar-bg">
    <div class="rsi-bar" style="width:{rv}%;{rbar}"></div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)

    # SFPs
    st.markdown('<div class="sec">Recent SFPs</div>', unsafe_allow_html=True)
    if sfps:
        for s in reversed(sfps[-5:]):
            sc  = "sfp-bull" if s["type"]=="bullish" else "sfp-bear"
            arr = "&#9650;" if s["type"]=="bullish" else "&#9660;"
            st.markdown(f"""
<div class="sfp-row">
  <span class="{sc}">{arr} {s['type'].upper()}</span>
  <span class="sfp-price">{pfmt(s['price'],0)}</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:Share Tech Mono;font-size:0.65rem;color:#3a3a52;">No SFPs detected</div>',
                    unsafe_allow_html=True)

    # Fear & Greed
    st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec">Fear &amp; Greed</div>', unsafe_allow_html=True)
    if fg_val is not None:
        if fg_val >= 75:   fc = "#ff3355"
        elif fg_val >= 55: fc = "#f7931a"
        elif fg_val >= 45: fc = "#f7931a"
        elif fg_val >= 25: fc = "#6b6b8a"
        else:              fc = "#00e5a0"
        # SVG ring gauge
        circumference = 2 * 3.14159 * 36
        dash = fg_val / 100 * circumference
        st.markdown(f"""
<div class="fg-card">
  <div class="fg-ring-wrap">
    <svg width="90" height="90" viewBox="0 0 90 90">
      <circle cx="45" cy="45" r="36" fill="none" stroke="#1a1a28" stroke-width="6"/>
      <circle cx="45" cy="45" r="36" fill="none" stroke="{fc}" stroke-width="6"
        stroke-dasharray="{dash:.1f} {circumference:.1f}"
        stroke-dashoffset="{circumference/4:.1f}"
        style="filter:drop-shadow(0 0 6px {fc});"/>
    </svg>
    <div class="fg-num" style="color:{fc};text-shadow:0 0 12px {fc}66;">{fg_val}</div>
  </div>
  <div class="fg-label">{(fg_label or '').upper()}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:Share Tech Mono;font-size:0.65rem;color:#3a3a52;">API unavailable</div>',
                    unsafe_allow_html=True)

st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)

# ── ROW 3: Levels | Trade Setups | Manipulation ───────────────────────────────
r3a, r3b, r3c = st.columns([1, 1.5, 1])

with r3a:
    st.markdown('<div class="sec">Support Levels</div>', unsafe_allow_html=True)
    s_labels = ["Major Support","Strong Support","Critical Support"]
    for i, lvl in enumerate(sup_lvls):
        lbl = s_labels[i] if i < len(s_labels) else f"Support {i+1}"
        st.markdown(f"""
<div class="level-row level-sup">
  <span class="level-name">{lbl}</span>
  <span class="lp-sup">{pfmt(lvl,0)}</span>
</div>""", unsafe_allow_html=True)
    if not sup_lvls:
        st.markdown('<div style="font-family:Share Tech Mono;font-size:0.65rem;color:#3a3a52;">Insufficient data</div>', unsafe_allow_html=True)

    st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec">Resistance Levels</div>', unsafe_allow_html=True)
    r_labels = ["Immediate Res","Major Resistance","Strong Resistance"]
    for i, lvl in enumerate(res_lvls):
        lbl = r_labels[i] if i < len(r_labels) else f"Resistance {i+1}"
        st.markdown(f"""
<div class="level-row level-res">
  <span class="level-name">{lbl}</span>
  <span class="lp-res">{pfmt(lvl,0)}</span>
</div>""", unsafe_allow_html=True)
    if not res_lvls:
        st.markdown('<div style="font-family:Share Tech Mono;font-size:0.65rem;color:#3a3a52;">Insufficient data</div>', unsafe_allow_html=True)

with r3b:
    st.markdown('<div class="sec">Trade Setups — ATR Based</div>', unsafe_allow_html=True)
    if long_s:
        st.markdown(f"""
<div class="setup-box setup-long">
  <div class="setup-hdr">
    <span class="setup-tag">&#9650; LONG SETUP</span>
    <span class="setup-note">ATR-based levels</span>
  </div>
  <div class="setup-grid">
    <span class="sg-l">Entry Zone</span><span class="sg-v">{long_s['entry']}</span>
    <span class="sg-l">Stop Loss</span><span class="sg-v" style="color:#ff3355;">{long_s['sl']}</span>
    <span class="sg-l">TP1</span><span class="sg-v sg-tp">{long_s['tp1']}</span>
    <span class="sg-l">TP2</span><span class="sg-v sg-tp">{long_s['tp2']}</span>
    <span class="sg-l">TP3</span><span class="sg-v sg-tp">{long_s['tp3']}</span>
    <span class="sg-l">Risk/Reward</span><span class="sg-v sg-rr">{long_s['rr']}</span>
    <span class="sg-l">Invalidated</span><span class="sg-v sg-inv">below {long_s['invalid']}</span>
  </div>
</div>""", unsafe_allow_html=True)

    if short_s:
        st.markdown(f"""
<div class="setup-box setup-short">
  <div class="setup-hdr">
    <span class="setup-tag">&#9660; SHORT SETUP</span>
    <span class="setup-note">ATR-based levels</span>
  </div>
  <div class="setup-grid">
    <span class="sg-l">Entry Zone</span><span class="sg-v">{short_s['entry']}</span>
    <span class="sg-l">Stop Loss</span><span class="sg-v" style="color:#ff3355;">{short_s['sl']}</span>
    <span class="sg-l">TP1</span><span class="sg-v sg-tp">{short_s['tp1']}</span>
    <span class="sg-l">TP2</span><span class="sg-v sg-tp">{short_s['tp2']}</span>
    <span class="sg-l">TP3</span><span class="sg-v sg-tp">{short_s['tp3']}</span>
    <span class="sg-l">Risk/Reward</span><span class="sg-v sg-rr">{short_s['rr']}</span>
    <span class="sg-l">Invalidated</span><span class="sg-v sg-inv">above {short_s['invalid']}</span>
  </div>
</div>""", unsafe_allow_html=True)

with r3c:
    st.markdown('<div class="sec">Manipulation Detection</div>', unsafe_allow_html=True)
    icon_map = {"a-danger": "&#9888;", "a-warn": "&#9888;", "a-ok": "&#10003;"}
    for label, msg, cls in manip_alerts:
        icon = icon_map.get(cls, "&#9679;")
        st.markdown(f"""
<div class="alert-row {cls}">
  <span class="alert-icon">{icon}</span>
  <span class="alert-body"><strong>{label}</strong>{msg}</span>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)

# ── ROW 4: Arb + Order Book ───────────────────────────────────────────────────
r4a, r4b = st.columns(2)

with r4a:
    st.markdown('<div class="sec">Arbitrage Spread</div>', unsafe_allow_html=True)
    fig_arb = chart_arb(tickers)
    if fig_arb:
        st.plotly_chart(fig_arb, use_container_width=True, config={"displayModeBar": False})
    prices = {k: v["price"] for k, v in tickers.items() if v and v.get("price") is not None}
    if len(prices) >= 2:
        ref  = min(prices.values())
        rows = []
        for n, p in prices.items():
            d_usd = p - ref
            d_pct = d_usd / ref * 100
            rows.append({"Exchange": n, "Price": pfmt(p),
                         "Premium $": f"+${d_usd:.2f}" if d_usd>=0 else f"-${abs(d_usd):.2f}",
                         "Premium %": f"+{d_pct:.4f}%" if d_pct>=0 else f"{d_pct:.4f}%"})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

with r4b:
    st.markdown(f'<div class="sec">Order Book &nbsp;·&nbsp; {chart_ex}</div>', unsafe_allow_html=True)
    fig_ob = chart_orderbook(ob, chart_ex)
    if fig_ob:
        st.plotly_chart(fig_ob, use_container_width=True, config={"displayModeBar": False})
    if ob:
        bc, ac = st.columns(2)
        with bc:
            st.dataframe(pd.DataFrame(ob["bids"][:8], columns=["Bid","Size"]).round(2),
                         hide_index=True, use_container_width=True)
        with ac:
            st.dataframe(pd.DataFrame(ob["asks"][:8], columns=["Ask","Size"]).round(2),
                         hide_index=True, use_container_width=True)

st.markdown('<div class="grid-line"></div>', unsafe_allow_html=True)

# ── ROW 5: Outlook scenarios ───────────────────────────────────────────────────
if df is not None:
    st.markdown('<div class="sec">Short-Term Outlook</div>', unsafe_allow_html=True)
    ov_a, ov_b = st.columns(2)

    bull_count = sum(1 for _,_,_,b in signals if b=="bull")
    bear_count = sum(1 for _,_,_,b in signals if b=="bear")
    rsi_now    = calc_rsi(df["close"]).iloc[-1]
    atr_now    = (df["high"] - df["low"]).rolling(14).mean().iloc[-1]
    last_close = df["close"].iloc[-1]
    ema20_now  = calc_ema(df["close"], 20).iloc[-1]

    bias_bull = bull_count > bear_count
    bias_cls  = "sc-bull" if bias_bull else "sc-bear"
    bias_txt  = "BULLISH BIAS" if bias_bull else "BEARISH BIAS"

    with ov_a:
        st.markdown(f"""
<div class="scenario {bias_cls}">
  <div class="sc-title">{bias_txt} &nbsp;·&nbsp; {bull_count}/{len(signals)} signals bullish</div>
  <div class="sc-text">
    Price: {pfmt(last_close)} &nbsp;·&nbsp; ATR: {pfmt(atr_now,0)}<br>
    {bull_count} bullish vs {bear_count} bearish readings.<br>
    {"Long entries near support favored." if bias_bull else "Bearish signals dominant. Watch for breakdown."}
  </div>
</div>""", unsafe_allow_html=True)

    with ov_b:
        if rsi_now > 65:
            sc_txt = f"RSI at {rsi_now:.1f} — approaching overbought. Pullback to EMA20 ({pfmt(ema20_now,0)}) likely before continuation."
            sc_cls, sc_title = "sc-bear", "PULLBACK RISK"
        elif rsi_now < 35:
            sc_txt = f"RSI at {rsi_now:.1f} — near oversold. Potential bounce from zone. Confirm with volume spike."
            sc_cls, sc_title = "sc-bull", "BOUNCE POTENTIAL"
        else:
            sc_txt = f"RSI at {rsi_now:.1f} — neutral zone. Range-bound likely. Key levels define next directional move."
            sc_cls = "sc-bull" if bias_bull else "sc-bear"
            sc_title = "RANGE / WATCH"
        st.markdown(f"""
<div class="scenario {sc_cls}">
  <div class="sc-title">{sc_title}</div>
  <div class="sc-text">{sc_txt}</div>
</div>""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:Share Tech Mono;font-size:0.52rem;color:#1a1a28;
            text-align:center;margin-top:1.5rem;padding-top:0.6rem;
            border-top:1px solid #0f0f18;letter-spacing:0.12em;">
  BTC TERMINAL &nbsp;·&nbsp; CCXT DATA ENGINE &nbsp;·&nbsp; FOR INFORMATIONAL USE ONLY &nbsp;·&nbsp; NOT FINANCIAL ADVICE
</div>
""", unsafe_allow_html=True)
