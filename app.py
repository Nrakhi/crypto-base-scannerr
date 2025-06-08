import streamlit as st
import ccxt, pandas as pd, numpy as np, time

st.title("📊 Smart Money Base Scanner (Binance 1D)")

@st.cache_data(ttl=3600)
def get_data():
    ex = ccxt.binance()
    ex.load_markets()
    symbols = [s for s in ex.symbols if s.endswith('/USDT') and 'UP/' not in s and 'DOWN/' not in s]
    data = {}
    for sym in symbols:
        try:
            ohlcv = ex.fetch_ohlcv(sym, '1d', limit=100)
            df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
            df['ts'] = pd.to_datetime(df['ts'], unit='ms')
            data[sym] = df
        except:
            pass
        time.sleep(0.05)
    return data

def check_base(df):
    recent = df.tail(20)
    price_range = (recent.high - recent.low).mean()
    if price_range / recent.close.mean() > 0.03: return False
    vol_thr = df.vol.quantile(0.2)
    if recent.vol.mean() > vol_thr: return False
    return True

def detect_bos(df):
    sw = (df.high.shift(1) < df.high) & (df.high.shift(-1) < df.high)
    swings = df.loc[sw]
    if len(swings) < 2: return False
    return df.high.iloc[-1] > swings.high.iloc[-2]

st.write("Tap 'Scan Now' to find coins in base + dead volume + BOS")
if st.button("🔍 Scan Now"):
    st.info("Scanning... please wait 90–120 seconds")
    data = get_data()
    results = [sym for sym, df in data.items() if len(df)>=50 and check_base(df) and detect_bos(df)]
    if results:
        st.success(f"✅ Found {len(results)} coins:")
        st.write(results)
    else:
        st.warning("No matching coins found.")
