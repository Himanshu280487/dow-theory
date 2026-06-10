import pandas as pd
import yfinance as yf

# Load NSE stock list
url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
stocks = pd.read_csv(url)

symbols = stocks["SYMBOL"].head(10)

print(f"Testing {len(symbols)} stocks...\n")

for symbol in symbols:

    ticker = f"{symbol}.NS"

    try:
        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if len(df) < 60:
            continue

        highs = df["High"].squeeze()
        lows = df["Low"].squeeze()

        recent_high = float(highs.tail(20).max())
        previous_high = float(highs.iloc[-40:-20].max())

        recent_low = float(lows.tail(20).min())
        previous_low = float(lows.iloc[-40:-20].min())

        if recent_high > previous_high and recent_low > previous_low:
            trend = "UPTREND"

        elif recent_high < previous_high and recent_low < previous_low:
            trend = "DOWNTREND"

        else:
            trend = "SIDEWAYS"

        print(f"{ticker:20} {trend}")

    except Exception as e:
        print(f"{ticker:20} ERROR")
