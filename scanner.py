import yfinance as yf

symbol = "RELIANCE.NS"

df = yf.download(
    symbol,
    period="1y",
    auto_adjust=True,
    progress=False
)

highs = df["High"].tail(60)
lows = df["Low"].tail(60)

recent_high = highs[-20:].max()
previous_high = highs[-40:-20].max()

recent_low = lows[-20:].min()
previous_low = lows[-40:-20].min()

print(f"Recent High: {recent_high}")
print(f"Previous High: {previous_high}")

print(f"Recent Low: {recent_low}")
print(f"Previous Low: {previous_low}")

if recent_high > previous_high and recent_low > previous_low:
    print("UPTREND")

elif recent_high < previous_high and recent_low < previous_low:
    print("DOWNTREND")

else:
    print("SIDEWAYS")
