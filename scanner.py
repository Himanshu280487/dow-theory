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


# =========================================================
# TREND CHECK
# =========================================================

def is_uptrend(swing_highs, swing_lows):

    if len(swing_highs) < 2:
        return False

    if len(swing_lows) < 2:
        return False

    return (
        swing_highs[-1] > swing_highs[-2]
        and
        swing_lows[-1] > swing_lows[-2]
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

        print(f"Scanning {ticker}...")

        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        # Skip bad downloads
        if df.empty:
            continue

        # Handle MultiIndex columns returned by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required_cols = ["Open", "High", "Low", "Close"]

        if not all(col in df.columns for col in required_cols):
            print(f"Missing columns for {ticker}")
            continue

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

        close_price = float(df["Close"].iloc[-1])

        breakout_price = float(swing_highs[-1])
        stop_loss = float(swing_lows[-1])

        # Buy signal
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

    except Exception as e:

        print(f"Error processing {ticker}")
        print(e)

# =========================================================
# RESULTS
# =========================================================

print("\n" + "=" * 60)
print("DOW THEORY BUY SIGNALS")
print("=" * 60)

if not signals:

    print("No valid signals found today.")

    email_body = "No valid Dow Theory signals found today."

else:

    email_body = "DOW THEORY BUY SIGNALS\n\n"

    for s in signals:

        print(f"Ticker     : {s['ticker']}")
        print(f"Buy Above  : {s['buy']:.2f}")
        print(f"Close      : {s['close']:.2f}")
        print(f"Stop Loss  : {s['sl']:.2f}")
        print(f"Risk       : {s['risk']:.2f}%")
        print("-" * 50)

        email_body += (
            f"{s['ticker']}\n"
            f"BUY ABOVE : {s['buy']:.2f}\n"
            f"CLOSE     : {s['close']:.2f}\n"
            f"STOP LOSS : {s['sl']:.2f}\n"
            f"RISK      : {s['risk']:.2f}%\n"
            f"{'-'*40}\n\n"
        )

    print(f"\nTOTAL SIGNALS : {len(signals)}")

# =========================================================
# EMAIL
# =========================================================

try:

    from email_alert import send_email

    send_email(
        "Dow Theory Scanner Results",
        email_body
    )

    print("\nEmail function executed.")

except ImportError:

    print("\nemail_alert.py not found.")

except Exception as e:

    print(f"\nEmail error: {e}")
