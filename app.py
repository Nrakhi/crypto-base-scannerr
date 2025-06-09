import streamlit as st
import pandas as pd
import ccxt
import datetime

st.set_page_config(page_title="Base Builder Scanner", layout="wide")

st.title("🔍 Base Builder Scanner - Bybit")
st.caption("Scans coins forming a base (consolidation) with low volume on major support levels.")

# Initialize Bybit (no API key needed)
bybit = ccxt.bybit({'enableRateLimit': True})

# Get all Bybit USDT symbols
markets = bybit.load_markets()
symbols = [symbol for symbol in markets if symbol.endswith('/USDT') and 'SPOT' in markets[symbol]['type']]

# Streamlit UI
st.sidebar.subheader("Scanner Settings")
days = st.sidebar.slider("Base period (days)", 5, 30, 15)
volume_threshold = st.sidebar.slider("Max volume avg", 0, 5000000, 1000000)
scan_button = st.sidebar.button("🔍 Scan Now")

def is_consolidating(df, days, volume_threshold):
    recent = df[-days:]
    price_range = recent['high'].max() - recent['low'].min()
    if price_range / recent['close'].mean() > 0.1:  # more than 10% range
        return False
    if recent['volume'].mean() > volume_threshold:
        return False
    return True

if scan_button:
    results = []
    st.info("Scanning... please wait ⏳")

    for symbol in symbols:
        try:
            ohlcv = bybit.fetch_ohlcv(symbol, timeframe='1d', limit=days+5)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            if is_consolidating(df, days, volume_threshold):
                results.append(symbol)
        except Exception as e:
            continue  # skip symbols that fail

    if results:
        st.success(f"✅ Found {len(results)} base-forming coins:")
        for r in results:
            st.write(f"• {r}")
    else:
        st.warning("No suitable coins found with your settings.")
