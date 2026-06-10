import pandas as pd
import yfinance as yf


# =========================================================
# FIND SWING HIGHS / LOWS
# =========================================================

def get_swings(df):
    highs = []
    lows = []

    high_series = df["High"].squeeze()
    low_series = df["Low"].squeeze()

    for i in range(2, len(df) - 2):

        # Swing High
        if (
            high_series.iloc[i] > high_series.iloc[i - 1]
            and high_series.iloc[i] > high_series.iloc[i - 2]
            and high_series.iloc[i] > high_series.iloc[i + 1]
            and high_series.iloc[i] > high_series.iloc[i + 2]
        ):
            highs.append(float(high_series.iloc[i]))

        # Swing Low
        if (
            low_series.iloc[i] < low_series.iloc[i - 1]
            and low_series.iloc[i] < low_series.iloc[i - 2]
            and low_series.iloc[i] < low_series.iloc[i + 1]
            and low_series.iloc[i] < low_series.iloc[i + 2]
        ):
            lows.append(float(low_series.iloc[i]))

    return highs, lows


# =========================================================
# DOW THEORY TREND
# =========================================================

def get_trend(highs, lows):

    if len(highs) < 2 or len(lows) < 2:
        return "INSUFFICIENT_DATA"

    h1 = highs[-2]
    h2 = highs[-1]

    l1 = lows[-2]
    l2 = lows[-1]

    if h2 > h1 and l2 > l1:
        return "UPTREND"

    if h2 < h1 and l2 < l1:
        return "DOWNTREND"

    return "SIDEWAYS"


# =========================================================
# LOAD NSE STOCKS
# =========================================================

url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

stocks = pd.read_csv(url)

symbols = stocks["SYMBOL"].head(10)

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

        highs, lows = get_swings(df)

        trend = get_trend(highs, lows)

        print(f"{ticker:20} {trend}")

        if len(highs) >= 2 and len(lows) >= 2:

            print(
                f"   HH: {highs[-2]:.2f} -> {highs[-1]:.2f}"
            )

            print(
                f"   HL: {lows[-2]:.2f} -> {lows[-1]:.2f}"
            )

    except Exception as e:

        print(f"{ticker:20} ERROR")
        print(str(e))

print("\nSCAN COMPLETE")
