import yfinance as yf

symbol = "RELIANCE.NS"

df = yf.download(
    symbol,
    period="1y",
    auto_adjust=True,
    progress=False
)

print(symbol)
print(f"Rows downloaded: {len(df)}")
print(df.tail())
