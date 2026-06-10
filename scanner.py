import yfinance as yf

symbol = "RELIANCE.NS"

df = yf.download(
    symbol,
    period="1y",
    auto_adjust=True,
    progress=False
)

# Handle yfinance multi-index columns
highs = df["High"].squeeze()
lows = df["Low"].squeeze()

recent_high = float(highs.tail(20).max())
previous_high = float(highs.iloc[-40:-20].max())

recent_low = float(lows.tail(20).min())
previous_low = float(lows.iloc[-40:-20].min())

print(f"Recent High: {recent_high:.2f}")
print(f"Previous High: {previous_high:.2f}")

print(f"Recent Low: {recent_low:.2f}")
print(f"Previous Low: {previous_low:.2f}")

if recent_high > previous_high and recent_low > previous_low:
    trend = "UPTREND"

elif recent_high < previous_high and recent_low < previous_low:
    trend = "DOWNTREND"

else:
    trend = "SIDEWAYS"

print(f"\nTREND: {trend}")
