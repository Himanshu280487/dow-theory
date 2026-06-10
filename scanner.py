import pandas as pd
import yfinance as yf

# =========================================================
# SETTINGS
# =========================================================

SWING_WINDOW = 5
NUM_STOCKS = 10

# =========================================================
# FIND SWING HIGHS / LOWS
# =========================================================

def get_swings(df, window=5):

    highs = df["High"].squeeze()
    lows = df["Low"].squeeze()

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):

        current_high = highs.iloc[i]
        current_low = lows.iloc[i]

        left_highs = highs.iloc[i-window:i]
        right_highs = highs.iloc[i+1:i+window+1]

        left_lows = lows.iloc[i-window:i]
        right_lows = lows.iloc[i+1:i+window+1]

        # Swing High
        if (
            current_high > left_highs.max()
            and current_high > right_highs.max()
        ):
            swing_highs.append(float(current_high))

        # Swing Low
        if (
            current_low < left_lows.min()
            and current_low < right_lows.min()
        ):
            swing_lows.append(float(current_low))

    return swing_highs, swing_lows


# =========================================================
# DOW THEORY TREND
# =========================================================

def get_trend(highs, lows):

    if len(highs) < 3 or len(lows) < 3:
        return "INSUFFICIENT_DATA"

    h1, h2, h3 = highs[-3:]
    l1, l2, l3 = lows[-3:]

    # Higher Highs + Higher Lows
    if (
        h1 < h2 < h3
        and
        l1 < l2 < l3
    ):
        return "UPTREND"

    # Lower Highs + Lower Lows
    if (
        h1 > h2 > h3
        and
        l1 > l2 > l3
    ):
        return "DOWNTREND"

    return "SIDEWAYS"


# =========================================================
# LOAD NSE STOCKS
# =========================================================

url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

stocks = pd.read_csv(url)

symbols = stocks["SYMBOL"].head(NUM_STOCKS)

print(f"\nTesting {len(symbols)} stocks...\n")

# =========================================================
# SCAN
# =========================================================

for symbol in symbols:

    ticker = f"{symbol}.NS"

    try:

        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False,
        )

        if len(df) < 100:
            print(f"{ticker:20} INSUFFICIENT_DATA")
            continue

        swing_highs, swing_lows = get_swings(
            df,
            window=SWING_WINDOW
        )

        trend = get_trend(
            swing_highs,
            swing_lows
        )

        print(f"{ticker:20} {trend}")

        if len(swing_highs) >= 3:
            h1, h2, h3 = swing_highs[-3:]
            print(
                f"   Highs: {h1:.2f} -> {h2:.2f} -> {h3:.2f}"
            )

        if len(swing_lows) >= 3:
            l1, l2, l3 = swing_lows[-3:]
            print(
                f"   Lows : {l1:.2f} -> {l2:.2f} -> {l3:.2f}"
            )

    except Exception as e:

        print(f"{ticker:20} ERROR")
        print(str(e))

print("\nSCAN COMPLETE")
