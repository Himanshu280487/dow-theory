import pandas as pd
import yfinance as yf
from email_alert import send_email

# =========================
# SETTINGS
# =========================
SWING_WINDOW = 5

# =========================
# SWING DETECTION
# =========================
def get_swings(df, window=5):

    highs = df["High"].astype(float)
    lows = df["Low"].astype(float)

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):

        ch = float(highs.iloc[i])
        cl = float(lows.iloc[i])

        lh = float(highs.iloc[i - window:i].max())
        rh = float(highs.iloc[i + 1:i + window + 1].max())

        ll = float(lows.iloc[i - window:i].min())
        rl = float(lows.iloc[i + 1:i + window + 1].min())

        if ch > lh and ch > rh:
            swing_highs.append(ch)

        if cl < ll and cl < rl:
            swing_lows.append(cl)

    return swing_highs, swing_lows


# =========================
# TREND CHECK (HH-HL)
# =========================
def is_uptrend(highs, lows):

    if len(highs) < 2 or len(lows) < 2:
        return False

    return highs[-1] > highs[-2] and lows[-1] > lows[-2]


# =========================
# VOLUME CONFIRMATION
# =========================
def volume_confirmation(df):

    vol = df["Volume"].astype(float)

    avg_vol = vol.tail(20).mean()
    last_vol = vol.iloc[-1]

    return last_vol > avg_vol


# =========================
# LOAD NSE STOCKS
# =========================
url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
stocks = pd.read_csv(url)

symbols = stocks["SYMBOL"].dropna().astype(str).unique()

signals = []
watchlist = []

print(f"Total stocks: {len(symbols)}")


# =========================
# SCAN ALL STOCKS
# =========================
for symbol in symbols:

    ticker = f"{symbol}.NS"

    try:

        # -------------------------
        # MONTHLY TREND (PRIMARY)
        # -------------------------
        df_m = yf.download(ticker, period="5y", interval="1mo", progress=False)

        if df_m.empty or len(df_m) < 6:
            continue

        monthly_close = df_m["Close"].astype(float)
        monthly_uptrend = monthly_close.iloc[-1] > monthly_close.iloc[-6]

        if not monthly_uptrend:
            continue


        # -------------------------
        # WEEKLY TREND (SECONDARY)
        # -------------------------
        df_w = yf.download(ticker, period="2y", interval="1wk", progress=False)

        if df_w.empty or len(df_w) < 30:
            continue

        swing_highs_w, swing_lows_w = get_swings(df_w, SWING_WINDOW)

        if len(swing_highs_w) < 2 or len(swing_lows_w) < 2:
            continue

        if not is_uptrend(swing_highs_w, swing_lows_w):
            continue


        # -------------------------
        # DAILY (ENTRY)
        # -------------------------
        df_d = yf.download(ticker, period="1y", interval="1d", progress=False)

        if df_d.empty or len(df_d) < 100:
            continue

        swing_highs_d, swing_lows_d = get_swings(df_d, SWING_WINDOW)

        if len(swing_highs_d) < 2 or len(swing_lows_d) < 2:
            continue

        if not is_uptrend(swing_highs_d, swing_lows_d):
            continue


        close_price = float(df_d["Close"].iloc[-1])
        breakout_price = float(swing_highs_d[-1])
        stop_loss = float(swing_lows_d[-1])


        # -------------------------
        # VOLUME FILTER
        # -------------------------
        if not volume_confirmation(df_d):
            continue


        # -------------------------
        # WATCHLIST DISTANCE
        # -------------------------
        distance = ((close_price - breakout_price) / breakout_price) * 100

        watchlist.append({
            "ticker": ticker,
            "distance": distance
        })


        # -------------------------
        # BUY SIGNAL
        # -------------------------
        if close_price > breakout_price:

            risk = ((breakout_price - stop_loss) / breakout_price) * 100

            signals.append({
                "ticker": ticker,
                "buy": breakout_price,
                "close": close_price,
                "sl": stop_loss,
                "risk": risk
            })


    except Exception:
        continue


# =========================
# OUTPUT
# =========================
email_body = "MULTI-TIMEFRAME DOW THEORY SCANNER\n\n"

if not signals:
    email_body += "No buy signals today.\n\n"
else:
    for s in signals:
        email_body += (
            f"{s['ticker']}\n"
            f"BUY: {s['buy']:.2f}\n"
            f"CLOSE: {s['close']:.2f}\n"
            f"SL: {s['sl']:.2f}\n"
            f"RISK: {s['risk']:.2f}%\n"
            f"----------------------\n\n"
        )


# =========================
# TOP WATCHLIST
# =========================
watchlist = sorted(watchlist, key=lambda x: abs(x["distance"]))[:20]

email_body += "\nTOP WATCHLIST\n\n"

for w in watchlist:
    email_body += f"{w['ticker']} {w['distance']:.2f}%\n"


# =========================
# SEND EMAIL
# =========================
send_email("Multi-Timeframe Dow Theory Scanner", email_body)
