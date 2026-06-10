import pandas as pd
import yfinance as yf
from email_alert import send_email

# =========================
# SETTINGS
# =========================
SWING_WINDOW = 5
NUM_STOCKS = 10

# =========================
# SWING DETECTION
# =========================
def get_swings(df, window=10):

    highs = df["High"].astype(float)
    lows = df["Low"].astype(float)

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):

        current_high = float(highs.iloc[i])
        current_low = float(lows.iloc[i])

        left_high = float(highs.iloc[i-window:i].max())
        right_high = float(highs.iloc[i+1:i+window+1].max())

        left_low = float(lows.iloc[i-window:i].min())
        right_low = float(lows.iloc[i+1:i+window+1].min())

        if current_high > left_high and current_high > right_high:
            swing_highs.append(current_high)

        if current_low < left_low and current_low < right_low:
            swing_lows.append(current_low)

    return swing_highs, swing_lows


# =========================
# TREND CHECK
# =========================
def is_uptrend(highs, lows):

    if len(highs) < 2 or len(lows) < 2:
        return False

    return highs[-1] > highs[-2] and lows[-1] > lows[-2]


# =========================
# LOAD NSE STOCKS
# =========================
url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
stocks = pd.read_csv(url)

symbols = stocks["SYMBOL"].head(NUM_STOCKS)

signals = []
watchlist = []

# =========================
# SCAN LOOP
# =========================
for symbol in symbols:

    ticker = f"{symbol}.NS"

    try:

        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 100:
            continue

        swing_highs, swing_lows = get_swings(df, SWING_WINDOW)

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            continue

        if not is_uptrend(swing_highs, swing_lows):
            continue

        close_price = float(df["Close"].iloc[-1])
        breakout_price = float(swing_highs[-1])
        stop_loss = float(swing_lows[-1])

        distance = ((close_price - breakout_price) / breakout_price) * 100

        watchlist.append({
            "ticker": ticker,
            "distance": distance
        })

        if close_price > breakout_price:

            risk = ((breakout_price - stop_loss) / breakout_price) * 100

            signals.append({
                "ticker": ticker,
                "buy": breakout_price,
                "close": close_price,
                "sl": stop_loss,
                "risk": risk
            })

    except Exception as e:
        print(f"Error {ticker}: {e}")


# =========================
# OUTPUT
# =========================
email_body = "DOW THEORY BUY SIGNALS\n\n"

if not signals:
    email_body += "No valid signals found today.\n"
else:
    for s in signals:
        email_body += (
            f"{s['ticker']}\n"
            f"BUY ABOVE: {s['buy']:.2f}\n"
            f"CLOSE: {s['close']:.2f}\n"
            f"SL: {s['sl']:.2f}\n"
            f"RISK: {s['risk']:.2f}%\n"
            f"------------------------\n\n"
        )

watchlist = sorted(watchlist, key=lambda x: abs(x["distance"]))[:20]

email_body += "\nTOP WATCHLIST\n\n"

for w in watchlist:
    email_body += f"{w['ticker']} {w['distance']:.2f}%\n"

# =========================
# EMAIL
# =========================
send_email("Dow Theory Scanner Results", email_body)
