import pandas as pd
import yfinance as yf

# =========================================================
# SETTINGS
# =========================================================

SWING_WINDOW = 10
NUM_STOCKS = 10

# =========================================================
# SWING DETECTION
# =========================================================

def get_swings(df, window=5):

    highs = df["High"].squeeze()
    lows = df["Low"].squeeze()

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):

        current_high = highs.iloc[i]
        current_low = lows.iloc[i]

        if (
            current_high > highs.iloc[i-window:i].max()
            and
            current_high > highs.iloc[i+1:i+window+1].max()
        ):
            swing_highs.append(float(current_high))

        if (
            current_low < lows.iloc[i-window:i].min()
            and
            current_low < lows.iloc[i+1:i+window+1].min()
        ):
            swing_lows.append(float(current_low))

    return swing_highs, swing_lows

# =========================================================
# TREND
# =========================================================

def is_uptrend(highs, lows):

    if len(highs) < 2 or len(lows) < 2:
        return False

    return (
        highs[-1] > highs[-2]
        and
        lows[-1] > lows[-2]
    )

# =========================================================
# MAIN
# =========================================================

url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

stocks = pd.read_csv(url)

symbols = stocks["SYMBOL"].head(NUM_STOCKS)

signals = []

for symbol in symbols:

    ticker = f"{symbol}.NS"

    try:

        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if len(df) < 100:
            continue

        swing_highs, swing_lows = get_swings(
            df,
            SWING_WINDOW
        )

        if not is_uptrend(
            swing_highs,
            swing_lows
        ):
            continue

        close_price = float(
            df["Close"].squeeze().iloc[-1]
        )

        breakout_price = swing_highs[-1]
        stop_loss = swing_lows[-1]

        # BUY SIGNAL
        if close_price > breakout_price:

            risk_pct = (
                (breakout_price - stop_loss)
                / breakout_price
            ) * 100

            signals.append({
                "ticker": ticker,
                "buy": breakout_price,
                "close": close_price,
                "sl": stop_loss,
                "risk": risk_pct
            })

    except Exception:
        pass

# =========================================================
# RESULTS
# =========================================================

print("\nDOW THEORY BUY SIGNALS\n")

if not signals:

    print("No valid signals found today.")

email_body = "DOW THEORY BUY SIGNALS\n\n"

        email_body += f"""
        {s['ticker']}

        BUY ABOVE : {s['buy']:.2f}
        CLOSE     : {s['close']:.2f}
        STOP LOSS : {s['sl']:.2f}
        RISK      : {s['risk']:.2f}%

--------------------------------
"""

email_body = "No valid Dow Theory signals found today."

    print("-" * 50)
    print(f"\nTOTAL SIGNALS : {len(signals)}")
    from email_alert import send_email

    send_email(
        "Dow Theory Scanner Results",
        email_body
    )
